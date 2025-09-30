
# MCP Tool Usage Guide & Mandatory Protocols

## **PREAMBLE: THE IMPLEMENTER'S TOOLKIT**

This document is the definitive and authoritative guide to your advanced toolset. You are required to consult this guide to ensure you are using your tools to their full potential and in accordance with project protocols.

---

## **1. Core Planning & Analysis Tool**

### **Tool: `sequentialthinking`**

This is your primary and most critical tool. You **MUST** initiate this tool at the beginning of every single task to structure your thought process according to the **Mandatory Operational Loop**.

* **Usage Protocol**: Use this tool to execute the HYPOTHESIZE, INVESTIGATE, and ISOLATE & PLAN stages of your operational loop. Your thoughts should build upon each other, forming a clear, logical path from problem analysis to a precise implementation plan.

---

## **2. Research & Information Gathering Tools**

### **Tool Suite: `tavily`**

This suite is your interface to the project's repository and the outside world.

* **`tavily-crawl`**: Use this tool to read the full, up-to-date content of specific project files when their URL is known. This is the preferred method for the INVESTIGATE stage when examining existing code.
* **`tavily-search`**: Use this tool to find external documentation for libraries, APIs, or error messages when the answer is not within the project files.
* **`tavily-extract`**: After finding a relevant page with `tavily-search`, use this tool to pull the specific, clean text you need to complete your implementation.

### **Tool Suite: `context7`**

This is a specialized and preferred tool for library documentation.

* **`resolve-library-id` & `get-library-docs`**: This is the **preferred method** for fulfilling the "Dependency Research Protocol." Before resorting to a general `tavily-search`, you should first attempt to use these tools to find canonical documentation.

---

## **3. Advanced Analysis & Memory Tools**

### **Tool Suite: `memory` (Knowledge Graph)**

This suite is for building a mental model of complex systems. While not mandatory for every task, it is highly encouraged for complex refactoring or debugging.

* **`create_entities`, `create_relations`**: Use these to map out module dependencies during your investigation of a complex bug.
* **`search_nodes`**: Use this to recall previously mapped relationships to avoid re-investigating the same system architecture repeatedly.
