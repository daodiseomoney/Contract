"""
IFC Agent module for integrating OpenAI Agents SDK with IFC data.
This module provides AI-enhanced interaction with BIM/IFC file objects.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class IFCAgent:
    """
    IFC Agent implementation using OpenAI Agents SDK for enhanced interaction with IFC data.

    This class provides AI capabilities for interacting with IFC files based on the OpenAI
    Agents framework, allowing structured reasoning and access to BIM data.
    """

    def __init__(self):
        """Initialize the IFC Agent with OpenAI Agents SDK integration"""
        self.ifc_file = None
        self.client = None
        self.agent_executor = None
        self.openai_agents_available = False

        # Try to initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI()
            logger.debug("OpenAI client initialized successfully for IFC Agent")
        except (ImportError, Exception) as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.client = None

        # Try to import and initialize OpenAI Agents SDK
        try:
            import openai_agents
            self.openai_agents_available = True
        except ImportError:
            logger.warning("IFCAgent has limited functionality due to missing dependencies")
            self.openai_agents_available = False

    def load_ifc_file(self, file_path: str) -> bool:
        """
        Load an IFC file for the agent to process.

        Args:
            file_path: Path to the IFC file

        Returns:
            bool: True if file loaded successfully, False otherwise
        """
        try:
            import ifcopenshell
            self.ifc_file = ifcopenshell.open(file_path)
            
            # Initialize agent tools after loading the file
            if self.openai_agents_available and self.client:
                self._setup_agent()
                
            return True
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return False

    def _get_building_info_tool(self):
        """
        Create a Tool for extracting building information from the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not self.openai_agents_available or not self.ifc_file:
            return None

        try:
            from openai_agents.tools import Tool
            
            def get_building_info() -> Dict[str, Any]:
                """Extract basic building information from the IFC file."""
                # Get building from the IFC file
                buildings = self.ifc_file.by_type("IfcBuilding")
                building = buildings[0] if buildings else None
                
                # Get project data
                projects = self.ifc_file.by_type("IfcProject")
                project = projects[0] if projects else None
                
                result = {
                    "building_name": building.Name if building and building.Name else "Unknown",
                    "project_name": project.Name if project and project.Name else "Unknown",
                    "storey_count": len(self.ifc_file.by_type("IfcBuildingStorey")),
                    "element_count": len(self.ifc_file.by_type("IfcElement")),
                    "element_types": self._get_element_types()
                }
                
                return result
                
            return Tool(
                name="get_building_info",
                description="Get summary information about the building in the IFC file",
                function=get_building_info
            )
        except Exception as e:
            logger.error(f"Error creating building_info tool: {e}")
            return None

    def _get_element_types_tool(self):
        """
        Create a Tool for listing element types in the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not self.openai_agents_available or not self.ifc_file:
            return None

        try:
            from openai_agents.tools import Tool
            
            def get_element_types() -> List[str]:
                """Get all element types in the IFC file."""
                return self._get_element_types()
                
            return Tool(
                name="get_element_types",
                description="Get the list of all element types in the IFC file",
                function=get_element_types
            )
        except Exception as e:
            logger.error(f"Error creating element_types tool: {e}")
            return None

    def _get_elements_by_type_tool(self):
        """
        Create a Tool for retrieving elements of a specific type.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not self.openai_agents_available or not self.ifc_file:
            return None

        try:
            from openai_agents.tools import Tool
            
            def get_elements_by_type(element_type: str) -> List[Dict[str, Any]]:
                """
                Get elements of a specific type from the IFC file.

                Args:
                    element_type: IFC element type (e.g., "IfcWall", "IfcDoor")

                Returns:
                    List of element dictionaries
                """
                # Ensure type has "Ifc" prefix
                if not element_type.startswith("Ifc"):
                    element_type = f"Ifc{element_type}"

                try:
                    elements = self.ifc_file.by_type(element_type)
                    return [self._element_to_dict(element) for element in elements]
                except Exception as e:
                    logger.error(f"Error getting elements of type {element_type}: {str(e)}")
                    return []
                
            return Tool(
                name="get_elements_by_type",
                description="Get all elements of a specific type (e.g., 'IfcWall', 'IfcDoor')",
                function=get_elements_by_type,
                parameters={
                    "element_type": {
                        "type": "string",
                        "description": "The IFC element type to retrieve (e.g., 'IfcWall', 'Wall', 'IfcDoor', 'Door')"
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error creating elements_by_type tool: {e}")
            return None

    def _get_spatial_structure_tool(self):
        """
        Create a Tool for extracting the spatial structure from the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not self.openai_agents_available or not self.ifc_file:
            return None

        try:
            from openai_agents.tools import Tool
            
            def get_spatial_structure() -> Dict[str, Any]:
                """Extract the spatial structure from the IFC file."""
                # Get project, site, building, and stories
                projects = self.ifc_file.by_type("IfcProject")
                if not projects:
                    return {"error": "No project found in the IFC file"}
                
                project = projects[0]
                result = {
                    "name": project.Name if project.Name else "Unknown Project",
                    "sites": []
                }
                
                # Process the spatial hierarchy
                for rel in project.IsDecomposedBy:
                    for site in rel.RelatedObjects:
                        if site.is_a("IfcSite"):
                            site_data = process_spatial_element(site)
                            result["sites"].append(site_data)
                
                return result
                
                def process_spatial_element(element, level=0):
                    """Recursively process spatial elements."""
                    elem_data = {
                        "id": element.id(),
                        "type": element.is_a(),
                        "name": element.Name if element.Name else f"{element.is_a()}_{element.id()}",
                        "children": []
                    }
                    
                    # Add contained elements
                    if hasattr(element, "IsDecomposedBy"):
                        for rel in element.IsDecomposedBy:
                            for child in rel.RelatedObjects:
                                child_data = process_spatial_element(child, level + 1)
                                elem_data["children"].append(child_data)
                    
                    # For building stories, add contained elements like walls, doors, etc.
                    if element.is_a("IfcBuildingStorey") and hasattr(element, "get_inverse"):
                        for rel in element.get_inverse("ContainsElements"):
                            if rel.is_a("IfcRelContainedInSpatialStructure"):
                                for item in rel.RelatedElements:
                                    if item.is_a("IfcElement"):
                                        elem_data.setdefault("elements", []).append({
                                            "id": item.id(),
                                            "type": item.is_a(),
                                            "name": item.Name if item.Name else f"{item.is_a()}_{item.id()}"
                                        })
                    
                    return elem_data
                
            return Tool(
                name="get_spatial_structure",
                description="Get the hierarchical spatial structure of the building",
                function=get_spatial_structure
            )
        except Exception as e:
            logger.error(f"Error creating spatial_structure tool: {e}")
            return None

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about the IFC file using OpenAI Agents.

        Args:
            query: User query about the IFC file

        Returns:
            Dict containing the response and metadata
        """
        if not self.client:
            return {
                "response": "OpenAI client is not available. Please check your API key configuration.",
                "success": False
            }
            
        if not self.ifc_file:
            return {
                "response": "No IFC file is loaded. Please load an IFC file first.",
                "success": False
            }
            
        if self.openai_agents_available and self.agent_executor:
            try:
                # Use the Agent framework for structured analysis
                result = self.agent_executor.invoke({"input": query})
                return {
                    "response": result["output"],
                    "success": True,
                    "metadata": {
                        "agent_based": True,
                        "steps": result.get("intermediate_steps", [])
                    }
                }
            except Exception as e:
                logger.error(f"Error processing query with agent: {e}")
                # Fall back to standard OpenAI API
                pass
                
        # Fall back to standard OpenAI API if agent not available or failed
        try:
            system_message = self._get_system_prompt()
            
            # Add context about the loaded IFC file
            building_context = "Unknown Building"
            projects = self.ifc_file.by_type("IfcProject")
            buildings = self.ifc_file.by_type("IfcBuilding")
            
            if projects:
                project_name = projects[0].Name if projects[0].Name else "Unknown Project"
                system_message += f"\n\nThe loaded IFC file contains project: {project_name}"
                
            if buildings:
                building_name = buildings[0].Name if buildings[0].Name else "Unknown Building"
                system_message += f"\nThe building name is: {building_name}"
                building_context = building_name
                
            element_counts = {}
            for element_type in self._get_element_types():
                count = len(self.ifc_file.by_type(element_type))
                if count > 0:
                    element_counts[element_type] = count
                    
            system_message += f"\n\nThe file contains the following elements: {element_counts}"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            return {
                "response": response.choices[0].message.content,
                "success": True,
                "metadata": {
                    "agent_based": False,
                    "context": {
                        "building": building_context,
                        "element_count": sum(element_counts.values())
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query with standard API: {e}")
            return {
                "response": f"Error processing your query: {str(e)}",
                "success": False
            }

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the IFC Agent.

        Returns:
            str: System prompt for the agent
        """
        return (
            "You are an AI assistant specialized in Building Information Modeling (BIM) and IFC files. "
            "You have expertise in architecture, construction, and building systems. Your purpose is to "
            "help users understand and analyze IFC/BIM data. You can answer questions about building elements, "
            "spatial structure, materials, and technical specifications found in IFC files."
            "\n\n"
            "When answering questions, be specific and professional. Cite actual data from the IFC file when available. "
            "If information is not available in the loaded IFC file, clearly state that."
        )
        
    def _setup_agent(self):
        """Set up the OpenAI Agent with appropriate tools for IFC analysis."""
        if not self.openai_agents_available or not self.client or not self.ifc_file:
            return
            
        try:
            from openai_agents import AgentExecutor
            from openai_agents.tools import Tool
            
            # Create tools
            tools = []
            
            building_info_tool = self._get_building_info_tool()
            if building_info_tool:
                tools.append(building_info_tool)
                
            element_types_tool = self._get_element_types_tool()
            if element_types_tool:
                tools.append(element_types_tool)
                
            elements_by_type_tool = self._get_elements_by_type_tool()
            if elements_by_type_tool:
                tools.append(elements_by_type_tool)
                
            spatial_structure_tool = self._get_spatial_structure_tool()
            if spatial_structure_tool:
                tools.append(spatial_structure_tool)
                
            # Create the agent
            self.agent_executor = AgentExecutor(
                tools=tools,
                llm=self.client,
                model="gpt-4o",
                system_prompt=self._get_system_prompt()
            )
            
            logger.info("IFC Agent initialized with OpenAI Agents SDK")
            
        except Exception as e:
            logger.error(f"Error setting up IFC agent: {e}")
            self.agent_executor = None
            
    def _get_element_types(self) -> List[str]:
        """Get all element types in the IFC file."""
        if not self.ifc_file:
            return []
            
        try:
            # Get all entity types that are subclasses of IfcElement
            entity_types = set()
            for element in self.ifc_file.by_type("IfcElement"):
                entity_types.add(element.is_a())
                
            return sorted(list(entity_types))
        except Exception as e:
            logger.error(f"Error getting element types: {e}")
            return []
            
    def _element_to_dict(self, element: Any) -> Dict:
        """Convert an IFC element to a dictionary representation."""
        try:
            # Basic properties
            result = {
                "id": element.id(),
                "type": element.is_a(),
                "name": element.Name if hasattr(element, "Name") and element.Name else f"{element.is_a()}_{element.id()}"
            }
            
            # Add GlobalId if available
            if hasattr(element, "GlobalId"):
                result["global_id"] = element.GlobalId
                
            # Add other properties based on element type
            if element.is_a("IfcWall"):
                result["element_type"] = "Wall"
            elif element.is_a("IfcDoor"):
                result["element_type"] = "Door"
            elif element.is_a("IfcWindow"):
                result["element_type"] = "Window"
            elif element.is_a("IfcSlab"):
                result["element_type"] = "Slab"
            elif element.is_a("IfcColumn"):
                result["element_type"] = "Column"
            elif element.is_a("IfcBeam"):
                result["element_type"] = "Beam"
                
            return result
        except Exception as e:
            logger.error(f"Error converting element to dict: {e}")
            return {"id": "unknown", "type": "unknown", "name": "Error in conversion"}