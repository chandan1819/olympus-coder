"""
Response validation utilities for Olympus-Coder-v1.

Validates JSON schema for tool requests, response formats, and error detection.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError, Draft7Validator


class ToolRequestValidator:
    """Validates tool request JSON outputs according to schema requirements."""
    
    # JSON schema for tool requests as per requirement 3.2
    TOOL_REQUEST_SCHEMA = {
        "type": "object",
        "properties": {
            "tool_name": {
                "type": "string",
                "minLength": 1
            },
            "parameters": {
                "type": "object"
            }
        },
        "required": ["tool_name", "parameters"],
        "additionalProperties": False
    }
    
    def __init__(self):
        self.validator = Draft7Validator(self.TOOL_REQUEST_SCHEMA)
    
    def validate_tool_request(self, response: str) -> Dict[str, Any]:
        """
        Validate a tool request JSON string.
        
        Args:
            response: JSON string containing tool request
            
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool
            - parsed_json: dict or None
            - errors: list of error messages
            - confidence_score: float (0.0 to 1.0)
        """
        result = {
            "is_valid": False,
            "parsed_json": None,
            "errors": [],
            "confidence_score": 0.0
        }
        
        try:
            # Parse JSON
            parsed = json.loads(response.strip())
            result["parsed_json"] = parsed
            
            # Validate against schema
            self.validator.validate(parsed)
            
            # Additional validation checks
            tool_name = parsed.get("tool_name", "")
            parameters = parsed.get("parameters", {})
            
            # Check tool name is not empty
            if not tool_name or not isinstance(tool_name, str):
                result["errors"].append("tool_name must be a non-empty string")
                return result
            
            # Check parameters is a dict
            if not isinstance(parameters, dict):
                result["errors"].append("parameters must be an object/dictionary")
                return result
            
            # Calculate confidence score based on completeness
            confidence = 1.0
            if not tool_name:
                confidence -= 0.5
            if not parameters:
                confidence -= 0.2
                
            result["is_valid"] = True
            result["confidence_score"] = max(0.0, confidence)
            
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON: {str(e)}")
        except ValidationError as e:
            result["errors"].append(f"Schema validation failed: {e.message}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {str(e)}")
        
        return result
    
    def extract_tool_requests(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract and validate all tool requests from a response.
        
        Args:
            response: Full model response that may contain tool requests
            
        Returns:
            List of validation results for each found tool request
        """
        results = []
        
        # Look for JSON objects in the response
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response)
        
        for match in matches:
            validation_result = self.validate_tool_request(match)
            if validation_result["is_valid"]:
                results.append(validation_result)
        
        return results


class ResponseValidator:
    """Validates overall model response format and structure."""
    
    def __init__(self):
        self.tool_validator = ToolRequestValidator()
    
    def validate_response_format(self, response: str) -> Dict[str, Any]:
        """
        Validate the overall format of a model response.
        
        Args:
            response: Full model response string
            
        Returns:
            Dict containing validation results
        """
        result = {
            "is_valid": True,
            "response_type": "unknown",
            "has_code_blocks": False,
            "has_tool_requests": False,
            "code_blocks": [],
            "tool_requests": [],
            "errors": [],
            "warnings": []
        }
        
        # Check for code blocks
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        code_matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if code_matches:
            result["has_code_blocks"] = True
            result["response_type"] = "code"
            for lang, code in code_matches:
                result["code_blocks"].append({
                    "language": lang or "unknown",
                    "code": code.strip()
                })
        
        # Check for tool requests
        tool_requests = self.tool_validator.extract_tool_requests(response)
        if tool_requests:
            result["has_tool_requests"] = True
            result["response_type"] = "tool_request"
            result["tool_requests"] = tool_requests
        
        # Validate response type consistency
        if result["has_code_blocks"] and result["has_tool_requests"]:
            result["warnings"].append(
                "Response contains both code blocks and tool requests - may indicate mixed response type"
            )
        
        # Check for empty response
        if not response.strip():
            result["is_valid"] = False
            result["errors"].append("Empty response")
        
        return result
    
    def check_structured_response_accuracy(self, responses: List[str]) -> float:
        """
        Calculate structured response accuracy across multiple responses.
        Target: >95% accuracy as per requirement 3.4.
        
        Args:
            responses: List of model responses to evaluate
            
        Returns:
            Accuracy score as float between 0.0 and 1.0
        """
        if not responses:
            return 0.0
        
        valid_count = 0
        total_count = len(responses)
        
        for response in responses:
            validation_result = self.validate_response_format(response)
            if validation_result["is_valid"]:
                valid_count += 1
        
        return valid_count / total_count