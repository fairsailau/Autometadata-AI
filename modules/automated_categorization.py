"""
Automated categorization workflow module.
This module handles document categorization with confidence scoring and routing.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Union
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCategorizationEngine:
    """
    Enhanced document categorization with multi-factor confidence scoring.
    """
    
    def __init__(self, client=None):
        """
        Initialize the categorization engine.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.confidence_threshold = 0.7
        self.category_history = {}
        self.history_lock = threading.RLock()
        self.history_path = os.path.join(os.path.dirname(__file__), '..', '.category_history.json')
        self._load_history()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set the confidence threshold.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            logger.warning(f"Invalid confidence threshold: {threshold}, must be between 0.0 and 1.0")
    
    def _load_history(self):
        """Load categorization history from file."""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    self.category_history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading category history: {str(e)}")
                self.category_history = {}
    
    def _save_history(self):
        """Save categorization history to file."""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.category_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving category history: {str(e)}")
    
    def categorize_document(self, file_id: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Categorize a document with enhanced confidence scoring.
        
        Args:
            file_id: Box file ID
            file_name: File name (optional, for pattern matching)
            
        Returns:
            dict: Categorization result with confidence metrics
        """
        if not self.client:
            logger.error("Box client not initialized")
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "confidence_factors": {},
                "requires_review": True,
                "error": "Box client not initialized"
            }
        
        try:
            # First-stage categorization
            first_stage = self._perform_first_stage_categorization(file_id)
            
            # Check confidence
            if first_stage["confidence"] >= self.confidence_threshold:
                # High confidence, return result
                return first_stage
            
            # Low confidence, perform second-stage categorization
            logger.info(f"Low confidence ({first_stage['confidence']:.2f}) for file {file_id}, performing second-stage categorization")
            second_stage = self._perform_second_stage_categorization(file_id, first_stage)
            
            # Combine results
            combined = self._combine_categorization_results(first_stage, second_stage)
            
            # Update history
            self._update_category_history(file_id, file_name, combined)
            
            return combined
        
        except Exception as e:
            logger.error(f"Error categorizing document: {str(e)}")
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "confidence_factors": {},
                "requires_review": True,
                "error": str(e)
            }
    
    def _perform_first_stage_categorization(self, file_id: str) -> Dict[str, Any]:
        """
        Perform first-stage categorization.
        
        Args:
            file_id: Box file ID
            
        Returns:
            dict: Categorization result
        """
        try:
            # Get file info
            file_info = self.client.file(file_id).get()
            file_name = file_info.name
            
            # Check file extension for quick categorization
            extension = os.path.splitext(file_name)[1].lower()
            
            # Initialize confidence factors
            confidence_factors = {
                "ai_confidence": 0.0,
                "document_quality": 0.0,
                "category_distinctiveness": 0.0,
                "historical_performance": 0.0
            }
            
            # Use Box AI for categorization
            ai_result = self._categorize_with_box_ai(file_id)
            
            # Extract category and confidence
            category = ai_result.get("category", "Unknown")
            ai_confidence = ai_result.get("confidence", 0.0)
            
            # Calculate document quality factor
            document_quality = self._calculate_document_quality(file_id, extension)
            
            # Calculate category distinctiveness
            category_distinctiveness = self._calculate_category_distinctiveness(ai_result)
            
            # Calculate historical performance
            historical_performance = self._calculate_historical_performance(category, extension)
            
            # Update confidence factors
            confidence_factors["ai_confidence"] = ai_confidence
            confidence_factors["document_quality"] = document_quality
            confidence_factors["category_distinctiveness"] = category_distinctiveness
            confidence_factors["historical_performance"] = historical_performance
            
            # Calculate overall confidence
            weights = {
                "ai_confidence": 0.5,
                "document_quality": 0.2,
                "category_distinctiveness": 0.2,
                "historical_performance": 0.1
            }
            
            overall_confidence = sum(
                factor * weights[name]
                for name, factor in confidence_factors.items()
            )
            
            # Prepare result
            result = {
                "category": category,
                "confidence": overall_confidence,
                "confidence_factors": confidence_factors,
                "requires_review": overall_confidence < self.confidence_threshold,
                "reasoning": ai_result.get("reasoning", ""),
                "file_name": file_name,
                "file_id": file_id,
                "timestamp": datetime.now().isoformat(),
                "stage": "first"
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in first-stage categorization: {str(e)}")
            raise
    
    def _perform_second_stage_categorization(self, file_id: str, first_stage: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform second-stage categorization with more detailed analysis.
        
        Args:
            file_id: Box file ID
            first_stage: First-stage categorization result
            
        Returns:
            dict: Second-stage categorization result
        """
        try:
            # Get initial category
            initial_category = first_stage.get("category", "Unknown")
            
            # Use Box AI with specialized prompt
            ai_result = self._categorize_with_box_ai_detailed(file_id, initial_category)
            
            # Extract category and confidence
            category = ai_result.get("category", initial_category)
            ai_confidence = ai_result.get("confidence", 0.0)
            
            # Use same confidence factors structure
            confidence_factors = first_stage.get("confidence_factors", {}).copy()
            
            # Update AI confidence
            confidence_factors["ai_confidence"] = ai_confidence
            
            # Increase category distinctiveness if same category
            if category == initial_category:
                confidence_factors["category_distinctiveness"] = min(
                    1.0, 
                    confidence_factors.get("category_distinctiveness", 0.0) + 0.2
                )
            
            # Calculate overall confidence with higher weight for AI
            weights = {
                "ai_confidence": 0.6,
                "document_quality": 0.15,
                "category_distinctiveness": 0.15,
                "historical_performance": 0.1
            }
            
            overall_confidence = sum(
                factor * weights[name]
                for name, factor in confidence_factors.items()
            )
            
            # Prepare result
            result = {
                "category": category,
                "confidence": overall_confidence,
                "confidence_factors": confidence_factors,
                "requires_review": overall_confidence < self.confidence_threshold,
                "reasoning": ai_result.get("reasoning", ""),
                "file_name": first_stage.get("file_name", ""),
                "file_id": file_id,
                "timestamp": datetime.now().isoformat(),
                "stage": "second"
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in second-stage categorization: {str(e)}")
            # Return first stage result if second stage fails
            return first_stage
    
    def _combine_categorization_results(self, first_stage: Dict[str, Any], second_stage: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine results from both categorization stages.
        
        Args:
            first_stage: First-stage categorization result
            second_stage: Second-stage categorization result
            
        Returns:
            dict: Combined categorization result
        """
        # Use second stage category if available
        category = second_stage.get("category", first_stage.get("category", "Unknown"))
        
        # Use higher confidence
        confidence = max(
            first_stage.get("confidence", 0.0),
            second_stage.get("confidence", 0.0)
        )
        
        # Combine confidence factors
        confidence_factors = {}
        for factor in ["ai_confidence", "document_quality", "category_distinctiveness", "historical_performance"]:
            confidence_factors[factor] = max(
                first_stage.get("confidence_factors", {}).get(factor, 0.0),
                second_stage.get("confidence_factors", {}).get(factor, 0.0)
            )
        
        # Combine reasoning
        reasoning = second_stage.get("reasoning", first_stage.get("reasoning", ""))
        
        # Prepare combined result
        result = {
            "category": category,
            "confidence": confidence,
            "confidence_factors": confidence_factors,
            "requires_review": confidence < self.confidence_threshold,
            "reasoning": reasoning,
            "file_name": first_stage.get("file_name", ""),
            "file_id": first_stage.get("file_id", ""),
            "timestamp": datetime.now().isoformat(),
            "stage": "combined",
            "first_stage": first_stage,
            "second_stage": second_stage
        }
        
        return result
    
    def _categorize_with_box_ai(self, file_id: str) -> Dict[str, Any]:
        """
        Categorize document using Box AI.
        
        Args:
            file_id: Box file ID
            
        Returns:
            dict: Categorization result
        """
        try:
            # Import here to avoid circular imports
            from modules.document_categorization import categorize_document
            
            # Call existing categorization function
            result = categorize_document(self.client, file_id)
            
            # Extract category and confidence
            category = result.get("category", "Unknown")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "")
            
            return {
                "category": category,
                "confidence": confidence,
                "reasoning": reasoning
            }
        
        except Exception as e:
            logger.error(f"Error categorizing with Box AI: {str(e)}")
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }
    
    def _categorize_with_box_ai_detailed(self, file_id: str, initial_category: str) -> Dict[str, Any]:
        """
        Categorize document using Box AI with detailed prompt.
        
        Args:
            file_id: Box file ID
            initial_category: Initial category from first stage
            
        Returns:
            dict: Categorization result
        """
        try:
            # Import here to avoid circular imports
            from modules.metadata_extraction import extract_metadata
            
            # Define specialized prompt
            prompt = f"""
            Analyze this document in detail to determine its category.
            The initial categorization suggested it might be '{initial_category}', but we need a more thorough analysis.

            For each of the following categories, provide a score from 0-10 indicating how well the document matches that category, along with specific evidence from the document:

            Sales Contract, Invoices, Tax, Financial Report, Employment Contract, PII, Other

            Then provide your final categorization in the following format:
            Category: [selected category]
            Confidence: [confidence score between 0 and 1, where 1 is highest confidence]
            Reasoning: [detailed explanation with specific evidence from the document]
            """
            
            # Call Box AI with prompt
            result = extract_metadata(self.client, file_id, prompt)
            
            # Parse result to extract category, confidence, and reasoning
            text = result.get("extracted_text", "")
            
            # Extract category
            category = initial_category
            confidence = 0.5  # Default confidence
            reasoning = ""
            
            # Parse category
            category_match = re.search(r"Category:\s*([^\n]+)", text)
            if category_match:
                category = category_match.group(1).strip()
            
            # Parse confidence
            confidence_match = re.search(r"Confidence:\s*(0\.\d+|1\.0|1)", text)
            if confidence_match:
                try:
                    confidence = float(confidence_match.group(1))
                except:
                    pass
            
            # Parse reasoning
            reasoning_match = re.search(r"Reasoning:\s*([^\n]+(?:\n[^\n]+)*)", text)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            return {
                "category": category,
                "confidence": confidence,
                "reasoning": reasoning
            }
        
        except Exception as e:
            logger.error(f"Error categorizing with Box AI detailed: {str(e)}")
            return {
                "category": initial_category,
                "confidence": 0.4,  # Lower confidence due to error
                "reasoning": f"Error in detailed analysis: {str(e)}"
            }
    
    def _calculate_document_quality(self, file_id: str, extension: str) -> float:
        """
        Calculate document quality factor.
        
        Args:
            file_id: Box file ID
            extension: File extension
            
        Returns:
            float: Document quality factor (0.0-1.0)
        """
        # Default quality based on extension
        extension_quality = {
            ".pdf": 0.9,
            ".docx": 0.8,
            ".doc": 0.7,
            ".txt": 0.6,
            ".jpg": 0.5,
            ".jpeg": 0.5,
            ".png": 0.5,
            ".tiff": 0.5,
            ".tif": 0.5
        }
        
        # Get base quality from extension
        quality = extension_quality.get(extension.lower(), 0.5)
        
        # TODO: Implement more sophisticated quality assessment
        # For now, just use extension-based quality
        
        return quality
    
    def _calculate_category_distinctiveness(self, ai_result: Dict[str, Any]) -> float:
        """
        Calculate category distinctiveness factor.
        
        Args:
            ai_result: AI categorization result
            
        Returns:
            float: Category distinctiveness factor (0.0-1.0)
        """
        # Extract confidence
        confidence = ai_result.get("confidence", 0.0)
        
        # For now, use AI confidence as distinctiveness
        # TODO: Implement more sophisticated distinctiveness calculation
        
        return confidence
    
    def _calculate_historical_performance(self, category: str, extension: str) -> float:
        """
        Calculate historical performance factor.
        
        Args:
            category: Document category
            extension: File extension
            
        Returns:
            float: Historical performance factor (0.0-1.0)
        """
        with self.history_lock:
            # Check if we have history for this category
            if category not in self.category_history:
                return 0.5  # Default for new categories
            
            # Get category history
            history = self.category_history[category]
            
            # Check if we have history for this extension
            if extension not in history.get("extensions", {}):
                return 0.6  # Slightly higher for known category
            
            # Get extension history
            ext_history = history["extensions"][extension]
            
            # Calculate success rate
            total = ext_history.get("total", 0)
            correct = ext_history.get("correct", 0)
            
            if total == 0:
                return 0.6  # Default if no samples
            
            # Calculate success rate
            success_rate = correct / total
            
            # Scale to 0.4-1.0 range (minimum 0.4 even with poor history)
            return 0.4 + (success_rate * 0.6)
    
    def _update_category_history(self, file_id: str, file_name: Optional[str], result: Dict[str, Any]):
        """
        Update categorization history.
        
        Args:
            file_id: Box file ID
            file_name: File name
            result: Categorization result
        """
        with self.history_lock:
            category = result.get("category", "Unknown")
            confidence = result.get("confidence", 0.0)
            
            # Get extension
            extension = ""
            if file_name:
                extension = os.path.splitext(file_name)[1].lower()
            
            # Initialize category if not exists
            if category not in self.category_history:
                self.category_history[category] = {
                    "total": 0,
                    "high_confidence": 0,
                    "extensions": {}
                }
            
            # Update category stats
            self.category_history[category]["total"] += 1
            if confidence >= self.confidence_threshold:
                self.category_history[category]["high_confidence"] += 1
            
            # Initialize extension if not exists
            if extension and extension not in self.category_history[category]["extensions"]:
                self.category_history[category]["extensions"][extension] = {
                    "total": 0,
                    "correct": 0
                }
            
            # Update extension stats
            if extension:
                self.category_history[category]["extensions"][extension]["total"] += 1
                
                # Assume correct if high confidence
                if confidence >= self.confidence_threshold:
                    self.category_history[category]["extensions"][extension]["correct"] += 1
            
            # Save history
            self._save_history()
    
    def update_categorization_feedback(self, file_id: str, original_category: str, 
                                      corrected_category: str, file_name: Optional[str] = None):
        """
        Update categorization history based on user feedback.
        
        Args:
            file_id: Box file ID
            original_category: Original category
            corrected_category: Corrected category
            file_name: File name
        """
        with self.history_lock:
            # Get extension
            extension = ""
            if file_name:
                extension = os.path.splitext(file_name)[1].lower()
            
            # Update original category stats (decrease correct count)
            if original_category in self.category_history and extension:
                if extension in self.category_history[original_category]["extensions"]:
                    ext_stats = self.category_history[original_category]["extensions"][extension]
                    if ext_stats["correct"] > 0:
                        ext_stats["correct"] -= 1
            
            # Initialize corrected category if not exists
            if corrected_category not in self.category_history:
                self.category_history[corrected_category] = {
                    "total": 0,
                    "high_confidence": 0,
                    "extensions": {}
                }
            
            # Update corrected category stats
            self.category_history[corrected_category]["total"] += 1
            
            # Initialize extension if not exists
            if extension and extension not in self.category_history[corrected_category]["extensions"]:
                self.category_history[corrected_category]["extensions"][extension] = {
                    "total": 0,
                    "correct": 0
                }
            
            # Update extension stats
            if extension:
                self.category_history[corrected_category]["extensions"][extension]["total"] += 1
                self.category_history[corrected_category]["extensions"][extension]["correct"] += 1
            
            # Save history
            self._save_history()
            
            logger.info(f"Updated categorization feedback: {original_category} -> {corrected_category}")


class WorkflowRouter:
    """
    Routes documents based on categorization results.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the workflow router.
        
        Args:
            confidence_threshold: Confidence threshold for automatic processing
        """
        self.confidence_threshold = confidence_threshold
        self.review_queue = []
        self.review_queue_lock = threading.RLock()
        self.review_queue_path = os.path.join(os.path.dirname(__file__), '..', '.review_queue.json')
        self._load_review_queue()
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set the confidence threshold.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            logger.warning(f"Invalid confidence threshold: {threshold}, must be between 0.0 and 1.0")
    
    def _load_review_queue(self):
        """Load review queue from file."""
        if os.path.exists(self.review_queue_path):
            try:
                with open(self.review_queue_path, 'r') as f:
                    self.review_queue = json.load(f)
            except Exception as e:
                logger.error(f"Error loading review queue: {str(e)}")
                self.review_queue = []
    
    def _save_review_queue(self):
        """Save review queue to file."""
        try:
            with open(self.review_queue_path, 'w') as f:
                json.dump(self.review_queue, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving review queue: {str(e)}")
    
    def route_document(self, categorization_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route document based on categorization result.
        
        Args:
            categorization_result: Categorization result
            
        Returns:
            dict: Routing result
        """
        # Extract confidence
        confidence = categorization_result.get("confidence", 0.0)
        requires_review = categorization_result.get("requires_review", True)
        
        # Determine route
        if confidence >= self.confidence_threshold and not requires_review:
            # High confidence, route to automated processing
            route = "automated"
        else:
            # Low confidence, route to manual review
            route = "manual_review"
            
            # Add to review queue
            self._add_to_review_queue(categorization_result)
        
        # Prepare routing result
        routing_result = {
            "route": route,
            "confidence": confidence,
            "confidence_threshold": self.confidence_threshold,
            "categorization": categorization_result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Routed document {categorization_result.get('file_id', 'unknown')} to {route} (confidence: {confidence:.2f})")
        
        return routing_result
    
    def _add_to_review_queue(self, categorization_result: Dict[str, Any]):
        """
        Add document to manual review queue.
        
        Args:
            categorization_result: Categorization result
        """
        with self.review_queue_lock:
            # Create review item
            review_item = {
                "file_id": categorization_result.get("file_id", ""),
                "file_name": categorization_result.get("file_name", ""),
                "category": categorization_result.get("category", "Unknown"),
                "confidence": categorization_result.get("confidence", 0.0),
                "reasoning": categorization_result.get("reasoning", ""),
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Add to queue
            self.review_queue.append(review_item)
            
            # Save queue
            self._save_review_queue()
            
            logger.info(f"Added document {review_item['file_id']} to review queue")
    
    def get_review_queue(self) -> List[Dict[str, Any]]:
        """
        Get the manual review queue.
        
        Returns:
            list: Review queue
        """
        with self.review_queue_lock:
            return self.review_queue.copy()
    
    def update_review_item(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a review item.
        
        Args:
            file_id: Box file ID
            updates: Updates to apply
            
        Returns:
            bool: True if item was updated, False otherwise
        """
        with self.review_queue_lock:
            # Find item
            for item in self.review_queue:
                if item["file_id"] == file_id:
                    # Apply updates
                    item.update(updates)
                    
                    # Save queue
                    self._save_review_queue()
                    
                    logger.info(f"Updated review item {file_id}")
                    return True
            
            logger.warning(f"Review item {file_id} not found")
            return False
    
    def remove_from_review_queue(self, file_id: str) -> bool:
        """
        Remove an item from the review queue.
        
        Args:
            file_id: Box file ID
            
        Returns:
            bool: True if item was removed, False otherwise
        """
        with self.review_queue_lock:
            # Find item
            for i, item in enumerate(self.review_queue):
                if item["file_id"] == file_id:
                    # Remove item
                    self.review_queue.pop(i)
                    
                    # Save queue
                    self._save_review_queue()
                    
                    logger.info(f"Removed review item {file_id}")
                    return True
            
            logger.warning(f"Review item {file_id} not found")
            return False


class AutomatedCategorization:
    """
    Automated categorization workflow.
    """
    
    def __init__(self, client=None, confidence_threshold: float = 0.7):
        """
        Initialize the automated categorization workflow.
        
        Args:
            client: Box client instance
            confidence_threshold: Confidence threshold for automatic processing
        """
        self.client = client
        self.categorization_engine = EnhancedCategorizationEngine(client)
        self.workflow_router = WorkflowRouter(confidence_threshold)
        
        # Set confidence threshold
        self.set_confidence_threshold(confidence_threshold)
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.categorization_engine.set_client(client)
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set the confidence threshold.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
        """
        self.categorization_engine.set_confidence_threshold(threshold)
        self.workflow_router.set_confidence_threshold(threshold)
    
    def process_file(self, file_id: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a file through the automated categorization workflow.
        
        Args:
            file_id: Box file ID
            file_name: File name (optional)
            
        Returns:
            dict: Processing result
        """
        try:
            # Get file info if name not provided
            if not file_name and self.client:
                try:
                    file_info = self.client.file(file_id).get()
                    file_name = file_info.name
                except Exception as e:
                    logger.warning(f"Error getting file info: {str(e)}")
            
            # Categorize document
            categorization_result = self.categorization_engine.categorize_document(file_id, file_name)
            
            # Route document
            routing_result = self.workflow_router.route_document(categorization_result)
            
            # Prepare processing result
            processing_result = {
                "file_id": file_id,
                "file_name": file_name,
                "categorization": categorization_result,
                "routing": routing_result,
                "timestamp": datetime.now().isoformat()
            }
            
            return processing_result
        
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                "file_id": file_id,
                "file_name": file_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_file_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a file event from Box webhook.
        
        Args:
            event: Box webhook event
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract file information from event
            source = event.get("source", {})
            file_id = source.get("id", "")
            file_name = source.get("name", "")
            
            if not file_id:
                logger.warning("Event has no file ID")
                return {
                    "error": "Event has no file ID",
                    "event": event,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Process file
            return self.process_file(file_id, file_name)
        
        except Exception as e:
            logger.error(f"Error processing file event: {str(e)}")
            return {
                "error": str(e),
                "event": event,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_review_queue(self) -> List[Dict[str, Any]]:
        """
        Get the manual review queue.
        
        Returns:
            list: Review queue
        """
        return self.workflow_router.get_review_queue()
    
    def update_review_item(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a review item.
        
        Args:
            file_id: Box file ID
            updates: Updates to apply
            
        Returns:
            bool: True if item was updated, False otherwise
        """
        return self.workflow_router.update_review_item(file_id, updates)
    
    def provide_categorization_feedback(self, file_id: str, original_category: str, 
                                       corrected_category: str, file_name: Optional[str] = None) -> bool:
        """
        Provide feedback on categorization.
        
        Args:
            file_id: Box file ID
            original_category: Original category
            corrected_category: Corrected category
            file_name: File name
            
        Returns:
            bool: True if feedback was processed, False otherwise
        """
        try:
            # Update categorization history
            self.categorization_engine.update_categorization_feedback(
                file_id, original_category, corrected_category, file_name
            )
            
            # Remove from review queue if present
            self.workflow_router.remove_from_review_queue(file_id)
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing categorization feedback: {str(e)}")
            return False


# Global instance
_automated_categorization = None

def get_automated_categorization(client=None, confidence_threshold: float = 0.7) -> AutomatedCategorization:
    """
    Get the global automated categorization instance.
    
    Args:
        client: Box client instance
        confidence_threshold: Confidence threshold for automatic processing
        
    Returns:
        AutomatedCategorization: Global automated categorization instance
    """
    global _automated_categorization
    
    if _automated_categorization is None:
        _automated_categorization = AutomatedCategorization(client, confidence_threshold)
    elif client is not None:
        _automated_categorization.set_client(client)
    
    return _automated_categorization

def process_file_upload_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a file upload event from Box webhook.
    
    Args:
        event: Box webhook event
        
    Returns:
        dict: Processing result
    """
    # Get automated categorization instance
    automated_categorization = get_automated_categorization()
    
    # Process event
    return automated_categorization.process_file_event(event)

# Import re module for regex
import re
