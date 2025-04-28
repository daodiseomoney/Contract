"""
IFC Agent module for integrating OpenAI Agents SDK with IFC data.
This module provides AI-enhanced interaction with BIM/IFC file objects.
"""

import logging
import os
import json  # noqa: F401
from typing import Dict, List, Optional, Any, Tuple

# Import IfcOpenShell if available
try:
    import ifcopenshell
    IFCOPENSHELL_AVAILABLE = True
except ImportError:
    IFCOPENSHELL_AVAILABLE = False
    logging.warning("IfcOpenShell not available. Some functionality will be limited.")

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI SDK not available. Some functionality will be limited.")

# Import OpenAI Agents SDK if available
try:
    from openai_agents import Tool, AgentExecutor, ChatCompletion
    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False
    logging.warning("OpenAI Agents SDK not available. Advanced IFC analysis will be limited.")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class IFCAgent:
    """
    IFC Agent implementation using OpenAI Agents SDK for enhanced interaction with IFC data.

    This class provides AI capabilities for interacting with IFC files based on the OpenAI
    Agents framework, allowing structured reasoning and access to BIM data.
    """

    def __init__(self):
        """Initialize the IFC Agent with OpenAI Agents SDK integration"""

        # Check dependencies
        self.deps_available = (
            IFCOPENSHELL_AVAILABLE and
            OPENAI_AVAILABLE and
            OPENAI_AGENTS_AVAILABLE
        )
        if not self.deps_available:
            logger.warning("IFCAgent has limited functionality due to missing dependencies")

        # Initialize OpenAI client if available
        self.client = None
        if OPENAI_AVAILABLE:
            try:
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    logger.warning("OPENAI_API_KEY not found in environment variables")
                else:
                    self.client = OpenAI(api_key=self.api_key)
                    logger.debug("OpenAI client initialized successfully for IFC Agent")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client for IFC Agent: {e}")

        # Current IFC file being processed
        self.ifc_file = None
        self.file_path = None

    def load_ifc_file(self, file_path: str) -> bool:
        """
        Load an IFC file for the agent to process.

        Args:
            file_path: Path to the IFC file

        Returns:
            bool: True if file loaded successfully, False otherwise
        """
        if not IFCOPENSHELL_AVAILABLE:
            logger.error("Cannot load IFC file: IfcOpenShell not available")
            return False

        try:
            logger.debug(f"IFC Agent loading file: {file_path}")
            self.ifc_file = ifcopenshell.open(file_path)
            self.file_path = file_path
            logger.info(f"IFC Agent successfully loaded file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"IFC Agent error loading file {file_path}: {str(e)}")
            return False

    def _get_building_info_tool(self):
        """
        Create a Tool for extracting building information from the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not OPENAI_AGENTS_AVAILABLE:
            return None

        def get_building_info() -> Dict[str, Any]:
            """Extract basic building information from the IFC file."""
            if not self.ifc_file:
                return {"error": "No IFC file loaded"}

            # Get building from the IFC file
            buildings = self.ifc_file.by_type("IfcBuilding")
            building = buildings[0] if buildings else None

            # Get building storey data
            storeys = self.ifc_file.by_type("IfcBuildingStorey")

            # Get project data
            projects = self.ifc_file.by_type("IfcProject")
            project = projects[0] if projects else None

            return {
                "file_name": os.path.basename(self.file_path) if self.file_path else "Unknown",
                "project_name": project.Name if project and project.Name else "Unknown Project",
                "building_name": building.Name if building and 
                    building.Name else "Unknown Building",
                "number_of_storeys": len(storeys),
                "element_count": sum(1 for _ in self.ifc_file.by_type("IfcElement")),
                "spaces_count": sum(1 for _ in self.ifc_file.by_type("IfcSpace")),
            }

        # Only create the Tool object if the SDK is available
        from openai_agents import Tool
        return Tool(
            name="get_building_info",
            description="Gets basic information about the building from the IFC file",
            function=get_building_info,
        )

    def _get_element_types_tool(self):
        """
        Create a Tool for listing element types in the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not OPENAI_AGENTS_AVAILABLE:
            return None

        def get_element_types() -> List[str]:
            """Get all element types in the IFC file."""
            if not self.ifc_file:
                return ["No IFC file loaded"]

            element_types = set()
            for element in self.ifc_file.by_type("IfcElement"):
                element_types.add(element.is_a())

            return sorted(list(element_types))

        # Only create the Tool object if the SDK is available
        from openai_agents import Tool
        return Tool(
            name="get_element_types",
            description="Gets all element types (wall, door, etc.) in the IFC file",
            function=get_element_types,
        )

    def _get_elements_by_type_tool(self):
        """
        Create a Tool for retrieving elements of a specific type.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not OPENAI_AGENTS_AVAILABLE:
            return None

        def get_elements_by_type(element_type: str) -> List[Dict[str, Any]]:
            """
            Get elements of a specific type from the IFC file.

            Args:
                element_type: IFC element type (e.g., "IfcWall", "IfcDoor")

            Returns:
                List of element dictionaries
            """
            if not self.ifc_file:
                return [{"error": "No IFC file loaded"}]

            try:
                elements = []
                for element in self.ifc_file.by_type(element_type):
                    # Extract basic properties
                    element_dict = {
                        "id": element.GlobalId,
                        "name": element.Name if hasattr(
                            element,
                            "Name"
                        ) and element.Name else "Unnamed",
                        "type": element.is_a(),
                    }

                    # Add properties if available
                    props = {}
                    for definition in self.ifc_file.get_inverse(element):
                        if definition.is_a("IfcRelDefinesByProperties"):
                            property_set = definition.RelatingPropertyDefinition
                            if property_set.is_a("IfcPropertySet"):
                                for prop in property_set.HasProperties:
                                    if prop.is_a("IfcPropertySingleValue"):
                                        if prop.NominalValue:
                                            props[prop.Name] = str(prop.NominalValue.wrappedValue)

                    element_dict["properties"] = props
                    elements.append(element_dict)

                return elements
            except Exception as e:
                logger.error(f"Error getting elements by type {element_type}: {str(e)}")
                return [{"error": f"Error retrieving elements: {str(e)}"}]

        # Only create the Tool object if the SDK is available
        from openai_agents import Tool
        return Tool(
            name="get_elements_by_type",
            description="Gets all elements of a specific type from the IFC file",
            function=get_elements_by_type,
            parameters=[
                {
                    "name": "element_type",
                    "type": "string",
                    "description": "IFC element type (e.g., IfcWall, IfcDoor)",
                    "required": True,
                }
            ],
        )

    def _get_spatial_structure_tool(self):
        """
        Create a Tool for extracting the spatial structure from the IFC file.

        Returns:
            Tool: An OpenAI Agents SDK Tool instance if available, else None
        """
        if not OPENAI_AGENTS_AVAILABLE:
            return None

        def get_spatial_structure() -> Dict[str, Any]:
            """Extract the spatial structure from the IFC file."""
            if not self.ifc_file:
                return {"error": "No IFC file loaded"}

            try:
                projects = self.ifc_file.by_type("IfcProject")
                if not projects:
                    return {"error": "No project found in IFC file"}

                project = projects[0]

                def process_spatial_element(element, level=0):
                    result = {
                        "id": element.GlobalId,
                        "name": element.Name if hasattr(
                            element,
                            "Name"
                        ) and element.Name else "Unnamed",
                        "type": element.is_a(),
                        "level": level,
                        "children": [],
                    }

                    # Find decomposition relationships
                    for rel in self.ifc_file.get_inverse(element):
                        if rel.is_a("IfcRelAggregates"):
                            if rel.RelatingObject == element:
                                for child in rel.RelatedObjects:
                                    result["children"].append(process_spatial_element(child, level + 1))

                    return result

                return process_spatial_element(project)
            except Exception as e:
                logger.error(f"Error getting spatial structure: {str(e)}")
                return {"error": f"Error retrieving spatial structure: {str(e)}"}

        # Only create the Tool object if the SDK is available
        from openai_agents import Tool
        return Tool(
            name="get_spatial_structure",
            description="Gets the spatial structure hierarchy from the IFC file",
            function=get_spatial_structure,
        )

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about the IFC file using OpenAI Agents.

        Args:
            query: User query about the IFC file

        Returns:
            Dict containing the response and metadata
        """
        # Check if all required dependencies are available
        if not self.deps_available:
            return {
                "success": False,
                "message": "Required dependencies (OpenAI Agents SDK) not available.",
            }

        if not self.client:
            return {
                "success": False,
                "message": "OpenAI client not available. Please check API key.",
            }

        if not self.ifc_file:
            return {
                "success": False,
                "message": "No IFC file loaded. Please load an IFC file first.",
            }

        try:
            # Create tools for the agent
            tools = []
            for tool_function in [
                self._get_building_info_tool,
                self._get_element_types_tool,
                self._get_elements_by_type_tool,
                self._get_spatial_structure_tool,
            ]:
                tool = tool_function()
                if tool:
                    tools.append(tool)

            # Check if we have any tools
            if not tools:
                return {
                    "success": False,
                    "message": "No tools available for the agent.",
                }

            # Import AgentExecutor here to avoid issues when the SDK is not available
            from openai_agents import AgentExecutor

            # Create agent with the tools
            agent = AgentExecutor(
                tools=tools,
                model="gpt-4o",
                system_prompt=self._get_system_prompt(),
            )

            # Execute the agent on the query
            logger.debug(f"Executing IFC Agent query: {query}")
            response = agent.execute(query)

            logger.debug(f"IFC Agent response: {response}")

            # Format the agent's response and include metadata
            return {
                "success": True,
                "response": response.get("output", "No response generated"),
                "ifc_file": os.path.basename(self.file_path) if self.file_path else None,
                "metadata": {
                    "tools_used": response.get("tools_used", []),
                    "model": "gpt-4o",
                }
            }

        except Exception as e:
            logger.error(f"Error processing query with IFC Agent: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
            }

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the IFC Agent.

        Returns:
            str: System prompt for the agent
        """
        return """
        You are an expert BIM (Building Information Modeling) assistant specialized in 
            analyzing IFC (Industry Foundation Classes) files.
        You help users extract meaningful insights from BIM models through detailed analysis of building elements, spatial structures, and properties.

        You have access to the following tools:
        - get_building_info: Provides basic information about the building like name,
            number of storeys, etc.
        - get_element_types: Lists all element types (wall, door, window, etc.) in the model
        - get_elements_by_type: Gets detailed information about elements of a specific type
        - get_spatial_structure: Shows the hierarchical spatial structure of the building

        Use these tools to answer queries about the building. First,
            determine which tools are needed to answer the user's question.
        Always provide specific,
            data-driven responses based on the actual IFC model content. Avoid making assumptions about
        the building that aren't supported by the data.

        For property analysis, focus on:
        - Spatial relationships and organization
        - Material specifications and quantities
        - Energy efficiency metrics
        - Building code compliance insights
        - Construction quality and specifications

        When responding,
            organize information clearly with appropriate formatting. If the data reveals issues or opportunities
        for improvement in the building design, highlight these in your response.
        """