"""LLM service for handling AI interactions."""

import os
import json
import re
import random
from typing import Dict, List, Optional

try:
    from langchain.chat_models import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain.chat_models import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

from langchain_core.prompts import PromptTemplate
from .langsmith_config import LangSmithConfig, get_langsmith_callbacks



class LLMService:
    """Service for LLM interactions using LangChain.

    By default prefers Google Gemini (via ChatGoogleGenerativeAI) when
    `GOOGLE_API_KEY` is available. Falls back to OpenAI when
    `OPENAI_API_KEY` is available. The default model can be overridden
    with the `LLM_MODEL` environment variable.
    """

    def __init__(self, model: Optional[str] = None, temperature: float = 0.7):
        """Initialize LLM service.

        Args:
            model: Optional model name. If not provided, `LLM_MODEL` env var is used
                   or defaults to `gemini-pro` for Google Gemini.
            temperature: Sampling temperature for the LLM.
        """
        self.model = model or os.getenv("LLM_MODEL", "gemini-pro")
        self.temperature = float(temperature)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        # Prefer Google Gemini if available
        if self.google_api_key and ChatGoogleGenerativeAI is not None:
            try:
                return ChatGoogleGenerativeAI(
                    model=self.model,
                    temperature=self.temperature,
                    google_api_key=self.google_api_key,
                )
            except TypeError:
                # Some LangChain wrappers accept different param names
                return ChatGoogleGenerativeAI(model=self.model, temperature=self.temperature)

        # Fallback to OpenAI if provided
        if self.openai_api_key and ChatOpenAI is not None:
            try:
                return ChatOpenAI(
                    model_name=self.model,
                    temperature=self.temperature,
                    openai_api_key=self.openai_api_key,
                )
            except TypeError:
                return ChatOpenAI(model=self.model, temperature=self.temperature)

        return None

    def _parse_json_response(self, response: str) -> Dict:
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "raw_response": response_text,
                "error": "Could not parse JSON"
            }

    def _run_chain(self, prompt_template: PromptTemplate, inputs: Dict) -> str:
       if not self.llm:
           raise RuntimeError("No LLM is configured. Set OPENAI_API_KEY or GOOGLE_API_KEY.")

       chain = prompt_template | self.llm
       
       # Use LangSmith callbacks if enabled
       callbacks = get_langsmith_callbacks()
       
       if callbacks:
           response = chain.invoke(inputs, config={"callbacks": callbacks})
       else:
           response = chain.invoke(inputs)
       
       return response.content

    def _normalize_role_name(self, role: str) -> str:
        """Normalize role name for consistent matching."""
        normalized = re.sub(r'\s*/\s*', '/', role.strip())
        return normalized
    
    def generate_topics(self, skills: List[str], technologies: List[str],
                        experience_years: int, domain_exposure: List[str],
                        role: str) -> List[str]:
        if not self.llm:
            return self._mock_topics(self._normalize_role_name(role))

        from ..prompts.prompts import TOPIC_GENERATION_PROMPT

        prompt = PromptTemplate(
            input_variables=["skills", "technologies", "experience_years", "domain_exposure", "role"],
            template=TOPIC_GENERATION_PROMPT
        )

        try:
            response = self._run_chain(
                prompt,
                {
                    "skills": ", ".join(skills),
                    "technologies": ", ".join(technologies),
                    "experience_years": experience_years,
                    "domain_exposure": ", ".join(domain_exposure),
                    "role": role
                }
            )
            parsed = self._parse_json_response(response)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "raw_response" in parsed:
                try:
                    start = parsed["raw_response"].find("[")
                    end = parsed["raw_response"].rfind("]") + 1
                    if start != -1 and end != 0:
                        return json.loads(parsed["raw_response"][start:end])
                except Exception:
                    pass
            return self._mock_topics(role)
        except Exception as e:
            print(f"Error generating topics: {e}")
            return self._mock_topics(role)

    def generate_question(self, topic: str, role: str, difficulty: str,
                          skills: List[str], experience_years: int,
                          retrieved_context: str) -> Dict:
        if not self.llm:
            return self._mock_question(topic, self._normalize_role_name(role), difficulty)

        from ..prompts.prompts import QUESTION_GENERATION_PROMPT

        prompt = PromptTemplate(
            input_variables=["topic", "role", "difficulty", "skills", "experience_years", "retrieved_context"],
            template=QUESTION_GENERATION_PROMPT
        )

        try:
            response = self._run_chain(
                prompt,
                {
                    "topic": topic,
                    "role": role,
                    "difficulty": difficulty,
                    "skills": ", ".join(skills),
                    "experience_years": experience_years,
                    "retrieved_context": retrieved_context
                }
            )
            parsed = self._parse_json_response(response)
            if isinstance(parsed, dict) and "question" in parsed:
                return parsed
            return self._mock_question(topic, role, difficulty)
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._mock_question(topic, role, difficulty)

    def evaluate_answer(self, question: str, answer: str, topic: str,
                        role: str, reference_context: str) -> Dict:
        if not self.llm:
            return self._mock_evaluation(answer, topic, reference_context)

        from ..prompts.prompts import ANSWER_EVALUATION_PROMPT

        prompt = PromptTemplate(
            input_variables=["question", "answer", "topic", "role", "reference_context"],
            template=ANSWER_EVALUATION_PROMPT
        )

        try:
            response = self._run_chain(
                prompt,
                {
                    "question": question,
                    "answer": answer,
                    "topic": topic,
                    "role": role,
                    "reference_context": reference_context
                }
            )
            parsed = self._parse_json_response(response)
            if isinstance(parsed, dict) and "score" in parsed:
                return parsed
            return self._mock_evaluation(answer, topic, reference_context)
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._mock_evaluation(answer, topic, reference_context)

    def _mock_topics(self, role: str) -> List[str]:
        topics_map = {
            "Backend Engineer": [
                "System Design Fundamentals",
                "Database Optimization",
                "API Design Patterns",
                "Scalability and Load Balancing",
                "Distributed Systems",
                "Caching Strategies",
                "Message Queues and Event Streaming",
                "Authentication and Authorization",
                "Database Transactions",
                "RESTful API Best Practices"
            ],
            "Frontend Engineer": [
                "React Component Design",
                "State Management",
                "Performance Optimization",
                "CSS and Responsive Design",
                "TypeScript Advanced Concepts",
                "Testing Strategies",
                "Accessibility (a11y)",
                "Build Tools and Bundling",
                "Browser Performance",
                "Web Security"
            ],
            "Full Stack Engineer": [
                "System Architecture",
                "Database Design",
                "Frontend Frameworks",
                "Backend API Development",
                "Deployment and DevOps",
                "Monitoring and Logging",
                "Security Best Practices",
                "Scalability",
                "Testing Strategies",
                "CI/CD Pipelines"
            ],
            "AI/ML Engineer": [
                "Machine Learning Fundamentals",
                "Deep Learning Architectures",
                "Feature Engineering",
                "Model Evaluation Metrics",
                "Production ML Systems",
                "Neural Networks",
                "NLP Techniques",
                "Computer Vision",
                "Data Preprocessing",
                "Model Deployment"
            ],
            "DevOps Engineer": [
                "Infrastructure as Code",
                "Container Orchestration",
                "CI/CD Pipelines",
                "Monitoring and Alerting",
                "Kubernetes Architecture",
                "Cloud Platforms",
                "Security and Compliance",
                "Logging and Observability",
                "Disaster Recovery",
                "Performance Tuning"
            ],
            "Data Scientist": [
                "Statistical Analysis",
                "Data Visualization",
                "Machine Learning Models",
                "Feature Engineering",
                "Data Cleaning and Preparation",
                "Predictive Analytics",
                "A/B Testing",
                "SQL and Databases",
                "Python for Data Science",
                "Business Acumen"
            ]
        }
        return topics_map.get(role, [
            "General Topic 1",
            "General Topic 2",
            "General Topic 3",
            "General Topic 4",
            "General Topic 5"
        ])

    def _mock_question(self, topic: str, role: str, difficulty: str) -> Dict:
        return {
            "question": f"Explain the key concepts of {topic} in the context of {role} role.",
            "context_used": "General knowledge",
            "expected_depth": difficulty
        }

    def _mock_evaluation(self, answer: str, topic: str, reference_context: str = "") -> Dict:
        """Generate intelligent mock evaluation with fair scoring based on answer quality."""
        answer_lower = answer.lower().strip()
        words = answer.split()
        word_count = len(words)
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        # ⚠️ HANDLE "I DON'T KNOW" OR EMPTY ANSWERS
        if not answer_lower or answer_lower in ["i dont know", "i don't know", "unknown", "not sure", "i'm not sure", "idk", "no idea"]:
            return {
                "score": 0.15,  # 1.5/10
                "accuracy": "Insufficient",
                "depth": "No content",
                "relevance": "Not addressed",
                "clarity": "Missing",
                "strengths": [],
                "weaknesses": ["No answer provided", "Question not addressed", "Insufficient knowledge demonstrated"],
                "feedback": "Your response does not address the question about " + topic + ". Please provide an answer that directly addresses the key concepts being asked.",
                "follow_up_suggestion": "Could you please provide a substantive answer about " + topic + "?"
            }
        
        # Comprehensive keyword mapping
        topic_keywords = {
            "Caching Strategies": {
                "core": ["cache", "caching", "redis", "memcached", "lru", "lfu", "ttl", "eviction", "in-memory", "latency", "performance"],
                "advanced": ["cache invalidation", "cache coherence", "distributed caching", "cache replacement", "write-through", "write-back"]
            },
            "Computer Vision": {
                "core": ["image", "vision", "object", "detection", "classification", "segmentation", "feature", "cnn"],
                "advanced": ["face recognition", "autonomous", "medical", "yolo", "rcnn", "semantic"]
            },
            "Neural Networks": {
                "core": ["layer", "neuron", "weight", "bias", "activation", "forward", "backpropagation", "optimization"],
                "advanced": ["gradient descent", "vanishing gradient", "normalization", "dropout", "regularization"]
            },
            "Feature Engineering": {
                "core": ["feature", "preprocessing", "cleaning", "encoding", "selection", "scaling", "normalization"],
                "advanced": ["dimensionality reduction", "pca", "outlier", "imputation", "transformation"]
            },
            "Model Deployment": {
                "core": ["deploy", "serving", "api", "docker", "scalability", "latency", "monitoring", "versioning"],
                "advanced": ["kubernetes", "containerization", "load balancing", "ci/cd", "blue-green"]
            },
            "Machine Learning Fundamentals": {
                "core": ["model", "training", "data", "accuracy", "performance", "evaluation", "metric"],
                "advanced": ["bias-variance", "overfitting", "underfitting", "validation", "cross-validation"]
            },
            "System Design Fundamentals": {
                "core": ["scalable", "architecture", "load", "distributed", "system", "design"],
                "advanced": ["tradeoff", "consistency", "availability", "fault tolerance", "redundancy"]
            },
            "Database Optimization": {
                "core": ["index", "query", "optimization", "normalization", "partition", "database"],
                "advanced": ["denormalization", "sharding", "replication", "transaction", "acid", "joins"]
            },
            "API Design Patterns": {
                "core": ["rest", "api", "endpoint", "http", "resource", "request", "response"],
                "advanced": ["graphql", "grpc", "async", "caching", "versioning", "rate limiting"]
            },
            "Scalability and Load Balancing": {
                "core": ["scalable", "load", "balance", "horizontal", "vertical", "cache"],
                "advanced": ["sharding", "replication", "clustering", "cdn", "caching strategies"]
            },
            "Distributed Systems": {
                "core": ["distributed", "consensus", "replication", "fault", "consistency", "system"],
                "advanced": ["byzantine", "eventual consistency", "consensus algorithms", "cap theorem"]
            },
            "NLP Techniques": {
                "core": ["nlp", "text", "language", "processing", "model", "embedding", "token"],
                "advanced": ["bert", "transformer", "sentiment", "translation", "question answering"]
            },
            "Deep Learning Architectures": {
                "core": ["neural", "network", "layer", "activation", "gradient", "deep"],
                "advanced": ["lstm", "gru", "transformer", "attention", "cnn", "rnn"]
            },
            "Model Evaluation Metrics": {
                "core": ["accuracy", "precision", "recall", "f1", "metric", "evaluation", "performance"],
                "advanced": ["auc", "roc", "confusion matrix", "pr curve", "threshold"]
            },
            "Production ML Systems": {
                "core": ["production", "deploy", "serving", "monitoring", "performance", "model"],
                "advanced": ["latency", "throughput", "scalability", "versioning", "ab testing"]
            },
            "Data Preprocessing": {
                "core": ["preprocessing", "cleaning", "missing", "normalization", "scaling", "data"],
                "advanced": ["imputation", "outlier detection", "balancing", "stratification"]
            },
            "Authentication and Authorization": {
                "core": ["authentication", "authorization", "identity", "password", "jwt", "token", "oauth", "permission", "access control"],
                "advanced": ["mfa", "sso", "role-based", "saml", "2fa", "encryption"]
            },
            "Database Transactions": {
                "core": ["transaction", "acid", "atomicity", "consistency", "isolation", "durability", "commit", "rollback"],
                "advanced": ["deadlock", "concurrency", "isolation level", "mvcc", "write-ahead logging"]
            },
            "Message Queues and Event Streaming": {
                "core": ["message", "queue", "event", "streaming", "producer", "consumer", "broker", "kafka", "rabbitmq"],
                "advanced": ["event sourcing", "exactly-once", "at-least-once", "partitioning", "offset"]
            },
            "RESTful API Best Practices": {
                "core": ["rest", "api", "http", "method", "status code", "resource", "endpoint", "stateless"],
                "advanced": ["versioning", "pagination", "rate limiting", "caching", "cors", "hypermedia"]
            }
        }
        
        # ⚠️ DETECT NONSENSICAL/CONTRADICTORY STATEMENTS (answers that are fundamentally wrong)
        nonsensical_patterns = {
            "RESTful API Best Practices": [
                "avoid.*status code",
                "random.*http.*method",
                "random.*method",
                "unpredictable.*api",
                "frontend.*color",
                "website.*design.*aesthetic",
                "ui.*animation",
                "logo.*design",
                "button.*form"
            ],
            "Message Queues and Event Streaming": [
                "ui.*animation",
                "offline.*without.*internet",
                "browser.*storage.*password",
                "skip.*server.*layer",
                "change.*color.*webpage",
                "frontend.*component",
                "synchronous.*queue",
                "synchronous.*message",
                "communicate.*synchronously",
                "strict.*blocking.*sequence",
                "avoid.*decoupling",
                "tight.*coupling",
                "tightly.*couple",
                "immediately.*drop",
                "immediately.*delete",
                "no.*persistence",
                "no.*acknowledge",
                "avoid.*acknowledgement",
                "no.*guarantee",
                "no.*storage",
                "no.*retry",
                "only.*first.*consumer",
                "single.*consumer",
                "permanently.*deleted",
                "cannot.*replay"
            ],
            "Scalability and Load Balancing": [
                "avoid.*scaling",
                "skip.*server",
                "reduce.*server",
                "fewer.*server",
                "reduce.*capacity",
                "reduce.*server.*traffic",
                "single.*server.*handle",
                "one.*server.*everything",
                "one.*process",
                "single.*machine",
                "avoid.*load.*balanc",
                "unnecessary.*complication",
                "avoid.*horizontal",
                "keep.*simple",
                "avoid.*distributed"
            ],
            "Caching Strategies": [
                "bypass.*cache",
                "avoid.*cache",
                "avoid.*redis",
                "avoid.*memcached",
                "cache.*grow.*indefinitely",
                "intentionally.*slower",
                "full.*table.*scan.*preferred",
                "avoid.*index",
                "avoid.*normalization",
                "duplicate.*data",
                "disable.*connection.*pool"
            ],
            "Database Optimization": [
                "intentionally.*slower",
                "avoid.*index",
                "full.*table.*scan.*preferred",
                "avoid.*normalization",
                "heavily.*duplicate",
                "complex.*query.*diversity",
                "disable.*connection.*pool",
                "new.*database.*connection.*request"
            ],
            "Distributed Systems": [
                "single.*machine",
                "no.*replication",
                "disable.*redundancy",
                "no.*fault.*tolerance",
                "single.*server.*handling.*everything",
                "single.*failure.*point",
                "partition.*irrelevant",
                "avoid.*networking",
                "in-memory.*function.*call"
            ],
            "Deep Learning Architectures": [
                "avoid.*layer",
                "flat.*model",
                "single.*layer.*perceptron.*all",
                "without.*convolution",
                "without.*spatial",
                "avoid.*rnn",
                "avoid.*memory",
                "avoid.*attention",
                "ignore.*time.*dependenc",
                "intentionally.*avoid.*hierarchical"
            ],
            "Production ML Systems": [
                "never.*update.*model",
                "avoid.*retraining",
                "deploy.*without.*test",
                "deploy.*without.*validat",
                "avoid.*data.*pipeline",
                "monitoring.*unnecessary",
                "raw.*uncleaned.*data",
                "ignore.*error",
                "avoid.*preprocessing",
                "avoid.*feature.*engineering"
            ],
            "Model Evaluation Metrics": [
                "avoid.*metric",
                "avoid.*accuracy",
                "avoid.*precision",
                "avoid.*recall",
                "avoid.*f1",
                "avoid.*confusion.*matrix",
                "intuition.*instead.*metric",
                "visual.*inspection",
                "ignore.*error.*measurement",
                "all.*prediction.*equally.*valid"
            ],
            "Neural Networks": [
                "should.*not.*use.*layer",
                "no.*multiple.*layer",
                "single.*layer.*sufficient",
                "avoid.*abstraction",
                "linear.*only",
                "no.*hidden.*layer",
                "avoid.*activation",
                "no.*backpropagation"
            ],
            "Feature Engineering": [
                "avoid.*feature.*selection",
                "avoid.*preprocessing",
                "raw.*data.*directly",
                "ignore.*outlier",
                "no.*scaling.*normalization",
                "avoid.*encoding",
                "ignore.*missing.*value"
            ],
            "Computer Vision": [
                "avoid.*convolution",
                "avoid.*pooling",
                "flatten.*all.*dimension",
                "pixel.*independent",
                "no.*spatial.*awareness",
                "avoid.*cnn"
            ],
            "NLP Techniques": [
                "ignore.*word.*order",
                "bag.*of.*word.*sufficient",
                "avoid.*embedding",
                "avoid.*transformer",
                "no.*context.*needed",
                "ignore.*sequence"
            ],
            "Machine Learning Fundamentals": [
                "avoid.*training",
                "random.*model.*best",
                "no.*validation.*needed",
                "ignore.*overfitting",
                "ignore.*underfitting",
                "avoid.*cross.*validation"
            ]
        }
        
        # Check for nonsensical patterns
        nonsensical_matches = 0
        if topic in nonsensical_patterns:
            for pattern in nonsensical_patterns[topic]:
                if re.search(pattern, answer_lower, re.IGNORECASE):
                    nonsensical_matches += 1
        
        # If multiple nonsensical statements found, answer is fundamentally wrong
        if nonsensical_matches >= 1:  # Even ONE nonsensical claim is problematic
            return {
                "score": 0.15,  # 1.5/10
                "accuracy": "Incorrect",
                "depth": "Fundamentally Flawed",
                "relevance": "Conceptually wrong",
                "clarity": "Misleading",
                "strengths": [],
                "weaknesses": ["Answer contains fundamentally incorrect concepts", "Contradicts core principles of the topic", "Demonstrates misunderstanding"],
                "feedback": "Your response contains significant technical inaccuracies. " + topic + " requires a different approach. Please review the core concepts.",
                "follow_up_suggestion": "Could you reconsider your answer with accurate understanding of " + topic + "?"
            }
        
        # ⚠️ KNOWLEDGE BASE CONTEXT VALIDATION
        # If we have knowledge base context, validate answer against it
        if reference_context and len(reference_context.strip()) > 0:
            context_lower = reference_context.lower()
            
            # Check if answer mentions concepts that directly contradict the knowledge base
            contradicting_concepts = []
            
            # Check for direct contradictions
            if ("index" in context_lower or "optimize" in context_lower) and "avoid.*index" in answer_lower:
                contradicting_concepts.append("contradicting indexing recommendations")
            if ("cache" in context_lower or "redis" in context_lower or "memcached" in context_lower) and ("bypass.*cache" in answer_lower or "avoid.*cache" in answer_lower):
                contradicting_concepts.append("contradicting caching strategy recommendations")
            if ("replica" in context_lower or "replication" in context_lower) and ("no.*replication" in answer_lower or "disable.*replication" in answer_lower):
                contradicting_concepts.append("contradicting replication principles from knowledge base")
            if ("redundancy" in context_lower or "fault.*tolerance" in context_lower) and ("disable.*redundancy" in answer_lower or "no.*fault.*tolerance" in answer_lower):
                contradicting_concepts.append("contradicting fault tolerance principles")
            if ("distributed" in context_lower or "partition" in context_lower) and ("single.*machine" in answer_lower or "no.*distribution" in answer_lower):
                contradicting_concepts.append("contradicting distributed system principles")
            
            if contradicting_concepts:
                return {
                    "score": 0.12,  # 1.2/10
                    "accuracy": "Incorrect (contradicts knowledge base)",
                    "depth": "Contradicts source material",
                    "relevance": "Opposite of documented practices",
                    "clarity": "Misleading",
                    "strengths": [],
                    "weaknesses": contradicting_concepts + ["Answer contradicts the knowledge base for this topic"],
                    "feedback": "Your answer directly contradicts the knowledge base material for " + topic + ". Please review the provided resources carefully.",
                    "follow_up_suggestion": "Please refer to the knowledge base materials for correct understanding of " + topic
                }
        
        # Get topic keywords
        relevant_keywords = topic_keywords.get(topic, {"core": [], "advanced": []})
        core_keywords = relevant_keywords.get("core", [])
        advanced_keywords = relevant_keywords.get("advanced", [])
        
        # Count exact matches
        core_hits = sum(1 for kw in core_keywords if kw in answer_lower)
        advanced_hits = sum(1 for kw in advanced_keywords if kw in answer_lower)
        
        # ⚠️ EARLY IRRELEVANCE CHECK: If almost NO core keywords found, answer is likely completely wrong
        if len(core_keywords) > 0 and core_hits == 0:
            # Answer has zero relevant keywords - completely off-topic
            return {
                "score": 0.15,  # Very low score for completely wrong answer
                "accuracy": "Incorrect",
                "depth": "Irrelevant",
                "relevance": "Completely irrelevant",
                "clarity": "Off-topic",
                "strengths": [],
                "weaknesses": ["Answer is not relevant to the topic", "No core concepts mentioned", "Completely off-topic"],
                "feedback": "Your response does not address the question about " + topic + ". Please provide an answer that directly addresses the key concepts being asked.",
                "follow_up_suggestion": "Could you please answer the question about " + topic + "? Focus on the core concepts."
            }
        
        # 1. RELEVANCE & COMPLETENESS (max +2.5 points)
        relevance_score = 0.0
        
        # Check if answer actually addresses the question
        if word_count < 20:
            relevance_score = 0.2  # Too brief
        elif word_count < 50:
            relevance_score = 0.8  # Minimal attempt
        elif word_count < 100:
            relevance_score = 1.5  # Good length
        else:
            relevance_score = 2.5  # Comprehensive
        
        # 2. TECHNICAL CONTENT (max +3.5 points) - CORE METRIC
        technical_score = 0.0
        
        # Score HEAVILY based on core keyword coverage - this is the real test of knowledge
        if len(core_keywords) > 0:
            core_ratio = core_hits / len(core_keywords)
            if core_ratio >= 0.85:
                technical_score += 2.8  # Excellent core knowledge (85%+)
            elif core_ratio >= 0.65:
                technical_score += 2.0  # Good core knowledge (65-85%)
            elif core_ratio >= 0.45:
                technical_score += 1.2  # Fair core knowledge (45-65%)
            elif core_ratio >= 0.25:
                technical_score += 0.5  # Basic core knowledge (25-45%)
            else:
                technical_score += 0.1  # Minimal (less than 25%)
        
        # Advanced keywords add bonus (not primary)
        if len(advanced_keywords) > 0 and advanced_hits > 0:
            advanced_ratio = advanced_hits / len(advanced_keywords)
            if advanced_ratio >= 0.7:
                technical_score += 0.7  # Strong advanced knowledge
            elif advanced_ratio >= 0.4:
                technical_score += 0.4  # Some advanced knowledge
            else:
                technical_score += 0.15  # Minimal advanced knowledge
        
        # 3. STRUCTURE & CLARITY (max +1.5 points)
        structure_score = 0.0
        
        # Multiple sentences = better structure
        if len(sentences) >= 5:
            structure_score += 0.9
        elif len(sentences) >= 3:
            structure_score += 0.5
        elif len(sentences) >= 2:
            structure_score += 0.2
        else:
            structure_score += 0.05
        
        # Specific indicators of good explanation
        good_phrases = [
            "for example", "such as", "instance", 
            "involve", "include", "process", "help",
            "improve", "enhance", "optimize",
            "understand", "explain", "demonstrate"
        ]
        phrase_count = sum(1 for phrase in good_phrases if phrase in answer_lower)
        structure_score += min(0.6, phrase_count * 0.12)
        
        # 4. DEPTH & SOPHISTICATION (max +2.5 points)
        depth_score = 0.0
        
        # Discussion of trade-offs, applications, or relationships
        sophistication_indicators = [
            "trade-off", "tradeoff", "pros and cons", "however", "moreover",
            "advantage", "disadvantage", "consider", "different approach",
            "application", "real-world", "scenario", "use case",
            "improve", "performance", "efficiency", "scalability"
        ]
        
        indicator_count = sum(1 for ind in sophistication_indicators if ind in answer_lower)
        if indicator_count >= 4:
            depth_score += 2.0  # Very sophisticated discussion
        elif indicator_count >= 2:
            depth_score += 1.2  # Some sophistication
        elif indicator_count >= 1:
            depth_score += 0.5  # Minimal sophistication
        else:
            depth_score += 0.1  # Surface level
        
        # Mention of tools/frameworks/specific techniques
        specific_tools = sum(1 for term in ["library", "framework", "tool", "algorithm", "model", "technique"] 
                            if term in answer_lower)
        depth_score += min(0.5, specific_tools * 0.2)
        
        # Calculate final score (0-10 scale, no base bonus)
        final_score = relevance_score + technical_score + structure_score + depth_score
        final_score = min(9.8, max(0.5, final_score))  # Cap between 0.5 and 9.8
        final_score = round(final_score, 1)  # Round to 1 decimal place for variety
        
        # FEEDBACK GENERATION based on actual score
        if final_score < 2.0:
            accuracy = "Poor"
            depth = "Minimal"
            feedback = "Your response is too brief and lacks technical content. Please provide a more comprehensive answer with specific technical concepts."
            strengths = ["Attempted to answer"]
            weaknesses = ["Too brief", "Missing key concepts", "Insufficient technical knowledge"]
        elif final_score < 3.5:
            accuracy = "Poor"
            depth = "Very Basic"
            feedback = "Your response covers very basic concepts but is missing most key technical knowledge. Please review the fundamentals."
            strengths = ["Some basic awareness"]
            weaknesses = ["Missing core concepts", "Superficial understanding", "Lacks technical depth"]
        elif final_score < 5.0:
            accuracy = "Fair"
            depth = "Basic"
            feedback = "Fair response covering some fundamentals, but lacks depth and misses important concepts. Add more technical details and examples."
            strengths = ["Covers some fundamentals", "Some relevant concepts mentioned"]
            weaknesses = ["Limited depth", "Missing technical details", "Needs examples"]
        elif final_score < 6.5:
            accuracy = "Good"
            depth = "Intermediate"
            feedback = "Good understanding demonstrated. To improve, include more technical details, discuss trade-offs, or provide real-world applications."
            strengths = ["Covers fundamentals well", "Clear explanation", "Relevant concepts"]
            weaknesses = ["Could add more depth", "Missing some advanced concepts", "Limited examples"]
        elif final_score < 8.0:
            accuracy = "Strong"
            depth = "Advanced"
            feedback = "Strong response! You've shown solid technical knowledge with good depth. Consider exploring edge cases or alternative approaches for even better coverage."
            strengths = ["Strong technical knowledge", "Clear explanation", "Good examples", "Well-structured answer"]
            weaknesses = ["Could explore more nuance", "Minor gaps in advanced topics"]
        else:
            accuracy = "Excellent"
            depth = "Comprehensive"
            feedback = "Excellent response! You've demonstrated comprehensive understanding with strong technical depth and excellent practical awareness."
            strengths = ["Comprehensive coverage", "Strong technical depth", "Excellent examples", "Sophisticated discussion", "Clear communication"]
            weaknesses = []
        
        return {
            "score": final_score / 10,  # Convert back to 0-1 for internal storage
            "accuracy": accuracy,
            "depth": depth,
            "relevance": "Highly relevant" if final_score > 6.5 else "Relevant" if final_score > 4.5 else "Somewhat relevant",
            "clarity": "Excellent" if final_score > 7.5 else "Good" if final_score > 5.5 else "Fair",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": feedback,
            "follow_up_suggestion": "Can you elaborate on trade-offs or advanced applications?" if final_score > 5.0 else "Could you provide specific examples or explain in more detail?"
        }
