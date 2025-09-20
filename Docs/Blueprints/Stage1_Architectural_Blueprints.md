# **STAGE 1 IMPLEMENTATION BLUEPRINTS**
## **Lead Architect's Detailed Technical Plans**

---

## **1. `app/core/P02_ProcessManager.py` - Real-Time Process Execution Engine**

### **Core Architecture Overview**
This module implements the "Maximum Debug" philosophy through non-blocking process execution with real-time callback streaming. The design centers around `asyncio` for concurrency and thread-safe PID management.

### **Data Structures & State Management**

```python
# Internal state management
class ProcessManager:
    def __init__(self):
        self._active_processes: Dict[str, Dict[str, Any]] = {}
        self._process_lock = asyncio.Lock()  # Thread-safe access to _active_processes
        self._pid_counter = 0  # Simple counter for unique process naming
```

**Process Tracking Structure:**
```python
# Each entry in _active_processes:
{
    "process_001": {
        "pid": 12345,
        "command": "pip install torch",
        "start_time": datetime.now(),
        "process_obj": <asyncio.subprocess.Process>,
        "status": "running"  # "running", "completed", "failed", "killed"
    }
}
```

### **Method Implementation Plans**

#### **`shell_run(command: str, callback: Callable[[str], None], cwd: Optional[str] = None) -> int`**

**Logical Flow:**
```python
def shell_run(self, command: str, callback: Callable[[str], None], cwd: Optional[str] = None) -> int:
    """
    IMPLEMENTATION PLAN:
    
    1. Generate unique process identifier
    2. Create asyncio subprocess with PIPE for stdout/stderr
    3. Store process in _active_processes with lock
    4. Launch concurrent _stream_output coroutine
    5. Wait for process completion
    6. Update process status and return exit code
    """
    
    # Step 1: Generate process ID and prepare
    process_id = f"process_{self._pid_counter:03d}"
    self._pid_counter += 1
    
    # Step 2: Asyncio subprocess creation
    # Use asyncio.create_subprocess_shell() with:
    # - stdout=asyncio.subprocess.PIPE
    # - stderr=asyncio.subprocess.PIPE  
    # - cwd=cwd if provided
    
    # Step 3: Store process info with async lock
    async with self._process_lock:
        self._active_processes[process_id] = {
            "pid": process.pid,
            "command": command,
            "start_time": datetime.now(),
            "process_obj": process,
            "status": "running"
        }
    
    # Step 4: Launch streaming task
    streaming_task = asyncio.create_task(
        self._stream_output(process, callback)
    )
    
    # Step 5: Wait for completion
    exit_code = await process.wait()
    await streaming_task  # Ensure all output is streamed
    
    # Step 6: Update status and cleanup
    async with self._process_lock:
        self._active_processes[process_id]["status"] = "completed" if exit_code == 0 else "failed"
    
    return exit_code
```

#### **`_stream_output(process, callback)` - The Critical Streaming Engine**

**Concurrent Output Reading Strategy:**
```python
async def _stream_output(self, process, callback):
    """
    IMPLEMENTATION PLAN:
    
    CHALLENGE: Read from both stdout and stderr concurrently without blocking
    SOLUTION: Use asyncio.gather() with separate coroutines for each stream
    
    Key Requirements:
    - Every line must trigger callback immediately
    - Must handle both stdout and stderr  
    - Must not block on either stream
    - Must continue until both streams are closed
    """
    
    async def read_stream(stream, stream_name):
        """Read from a single stream and callback each line"""
        try:
            while True:
                line = await stream.readline()
                if not line:  # Stream closed
                    break
                
                # Decode and clean the line
                decoded_line = line.decode('utf-8', errors='replace').rstrip('\n\r')
                
                # Prefix with stream type for clarity
                prefixed_line = f"[{stream_name}] {decoded_line}"
                
                # Invoke callback immediately
                callback(prefixed_line)
                
        except Exception as e:
            callback(f"[{stream_name}] Stream error: {str(e)}")
    
    # Launch both stream readers concurrently
    await asyncio.gather(
        read_stream(process.stdout, "stdout"),
        read_stream(process.stderr, "stderr"),
        return_exceptions=True  # Don't let one stream error kill the other
    )
```

#### **Thread-Safe PID Management**

```python
def get_active_processes(self) -> Dict[str, int]:
    """
    IMPLEMENTATION PLAN:
    
    Return snapshot of active processes as {process_name: pid}
    Must be thread-safe and filter out completed processes
    """
    active_snapshot = {}
    
    # Use asyncio.run_coroutine_threadsafe if called from non-async context
    async def _get_active():
        async with self._process_lock:
            for proc_id, proc_info in self._active_processes.items():
                if proc_info["status"] == "running":
                    active_snapshot[proc_id] = proc_info["pid"]
        return active_snapshot
    
    # Handle both async and sync calling contexts
    if asyncio.iscoroutinefunction(self.get_active_processes):
        return await _get_active()
    else:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_get_active())

def kill_process(self, pid: int) -> bool:
    """
    IMPLEMENTATION PLAN:
    
    1. Find process by PID in _active_processes
    2. Use process_obj.terminate() first (graceful)
    3. If still running after 5 seconds, use process_obj.kill() (force)
    4. Update status to "killed"
    5. Return success boolean
    """
    
    # Find process by PID
    target_process = None
    target_id = None
    
    async with self._process_lock:
        for proc_id, proc_info in self._active_processes.items():
            if proc_info["pid"] == pid and proc_info["status"] == "running":
                target_process = proc_info["process_obj"]
                target_id = proc_id
                break
    
    if not target_process:
        return False  # Process not found or not running
    
    # Graceful termination attempt
    target_process.terminate()
    
    # Wait up to 5 seconds for graceful shutdown
    try:
        await asyncio.wait_for(target_process.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        # Force kill if graceful termination failed
        target_process.kill()
        await target_process.wait()
    
    # Update status
    async with self._process_lock:
        self._active_processes[target_id]["status"] = "killed"
    
    return True
```

### **Error Handling Strategy**

```python
# Comprehensive error handling approach:

1. **Subprocess Creation Errors**: 
   - Catch FileNotFoundError, PermissionError
   - Log full exception and command that failed
   - Return exit code -1 for creation failures

2. **Stream Reading Errors**:
   - Use 'replace' mode for decode errors
   - Catch and log stream exceptions without terminating
   - Continue reading from other stream if one fails

3. **Process Termination Errors**:
   - Handle ProcessLookupError (process already dead)
   - Timeout handling for hung processes
   - Zombie process cleanup

4. **Thread Safety Errors**:
   - All _active_processes access protected by asyncio.Lock()
   - Exception handling in all async contexts
   - Graceful degradation if locking fails
```

---

## **2. `app/utils/P03_Translator.py` - Universal Installer Parser**

### **Core Architecture Overview**
This module converts diverse Pinokio installer formats into standardized Python recipes without requiring a Node.js runtime. The key challenge is parsing JavaScript using pure Python regex patterns.

### **Standardized Recipe Format**
```python
# Target output format for all parsers:
standardized_recipe = [
    {
        "step_type": "shell_run",  # "shell_run", "fs_download", "fs_copy", "input", etc.
        "params": {
            "command": "pip install torch",
            "args": [],
            "options": {}
        },
        "conditions": {},  # For conditional execution
        "error_handling": "stop"  # "stop", "continue", "retry"
    },
    {
        "step_type": "fs_download", 
        "params": {
            "url": "https://example.com/model.bin",
            "destination": "./models/model.bin",
            "checksum": "sha256:abc123..."
        }
    }
    # ... more steps
]
```

### **Method Implementation Plans**

#### **`parse_js(file_path: str) -> List[Dict[str, Any]]` - The JavaScript Parser**

**Core Challenge**: Extract Pinokio API calls from JavaScript without Node.js runtime.

**Regex Pattern Library:**
```python
class JavaScriptPatterns:
    """
    IMPLEMENTATION PLAN: Comprehensive regex library for Pinokio JS patterns
    """
    
    # Pattern 1: shell.run() calls
    SHELL_RUN_PATTERN = re.compile(
        r'shell\.run\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*(\{[^}]*\}))?\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    # Pattern 2: fs.download() calls  
    FS_DOWNLOAD_PATTERN = re.compile(
        r'fs\.download\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*(\{[^}]*\}))?\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    # Pattern 3: fs.copy() calls
    FS_COPY_PATTERN = re.compile(
        r'fs\.copy\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        re.MULTILINE
    )
    
    # Pattern 4: input() calls with prompts
    INPUT_PATTERN = re.compile(
        r'input\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]+)[\'"`])?\s*\)',
        re.MULTILINE
    )
    
    # Pattern 5: Conditional blocks (if statements)
    CONDITIONAL_PATTERN = re.compile(
        r'if\s*\(\s*([^)]+)\s*\)\s*\{([^}]*)\}',
        re.MULTILINE | re.DOTALL
    )
```

**JavaScript Parsing Logical Flow:**
```python
def parse_js(self, file_path: str) -> List[Dict[str, Any]]:
    """
    IMPLEMENTATION PLAN:
    
    Step 1: Read and preprocess JavaScript file
    Step 2: Apply regex patterns to extract API calls
    Step 3: Handle nested/conditional structures  
    Step 4: Convert to standardized format
    Step 5: Validate and return recipe
    """
    
    # Step 1: File preprocessing
    with open(file_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Remove comments and normalize whitespace
    js_content = self._preprocess_js(js_content)
    
    # Step 2: Extract all API calls using patterns
    extracted_calls = []
    
    # Extract shell.run calls
    for match in self.patterns.SHELL_RUN_PATTERN.finditer(js_content):
        command = match.group(1)
        options = match.group(2) if match.group(2) else "{}"
        
        extracted_calls.append({
            "raw_type": "shell.run",
            "command": command,
            "options": self._parse_js_object(options),
            "line_number": js_content[:match.start()].count('\n') + 1
        })
    
    # Extract fs.download calls
    for match in self.patterns.FS_DOWNLOAD_PATTERN.finditer(js_content):
        url = match.group(1) 
        destination = match.group(2)
        options = match.group(3) if match.group(3) else "{}"
        
        extracted_calls.append({
            "raw_type": "fs.download",
            "url": url,
            "destination": destination, 
            "options": self._parse_js_object(options),
            "line_number": js_content[:match.start()].count('\n') + 1
        })
    
    # Sort by line number to preserve execution order
    extracted_calls.sort(key=lambda x: x["line_number"])
    
    # Step 3: Handle conditionals (simplified approach)
    # For Phase P03, we'll treat conditionals as comments and extract inner content
    
    # Step 4: Convert to standardized format
    standardized_recipe = []
    for call in extracted_calls:
        standardized_step = self._standardize_step(call)
        if standardized_step:
            standardized_recipe.append(standardized_step)
    
    return standardized_recipe

def _preprocess_js(self, js_content: str) -> str:
    """
    IMPLEMENTATION PLAN: Clean JavaScript for better regex matching
    """
    # Remove single-line comments
    js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
    
    # Remove multi-line comments  
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    
    # Normalize whitespace around function calls
    js_content = re.sub(r'\s*\(\s*', '(', js_content)
    js_content = re.sub(r'\s*\)\s*', ')', js_content)
    
    return js_content

def _parse_js_object(self, js_obj_str: str) -> Dict[str, Any]:
    """
    IMPLEMENTATION PLAN: Parse simple JavaScript object literals
    
    LIMITATION: This is a simplified parser for basic objects.
    It won't handle complex nested objects or functions.
    """
    if not js_obj_str or js_obj_str.strip() == "{}":
        return {}
    
    # Simple key-value extraction for basic objects
    # Example: {cwd: "./models", timeout: 30}
    obj_pattern = re.compile(r'(\w+)\s*:\s*([\'"`]?)([^,}]+)\2')
    
    result = {}
    for match in obj_pattern.finditer(js_obj_str):
        key = match.group(1)
        value = match.group(3).strip()
        
        # Try to convert to appropriate Python type
        if value.isdigit():
            result[key] = int(value)
        elif value in ['true', 'false']:
            result[key] = value == 'true'
        else:
            result[key] = value
    
    return result
```

#### **`_standardize_step(step_data: Dict[str, Any]) -> Dict[str, Any]`**

**Conversion Logic:**
```python
def _standardize_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    IMPLEMENTATION PLAN: Convert raw parsed data to standardized format
    """
    
    raw_type = step_data["raw_type"]
    
    if raw_type == "shell.run":
        return {
            "step_type": "shell_run",
            "params": {
                "command": step_data["command"],
                "args": [],
                "options": step_data.get("options", {})
            },
            "conditions": {},
            "error_handling": "stop"
        }
    
    elif raw_type == "fs.download":
        return {
            "step_type": "fs_download", 
            "params": {
                "url": step_data["url"],
                "destination": step_data["destination"],
                "checksum": step_data.get("options", {}).get("checksum"),
                "options": step_data.get("options", {})
            },
            "conditions": {},
            "error_handling": "stop"
        }
    
    elif raw_type == "fs.copy":
        return {
            "step_type": "fs_copy",
            "params": {
                "source": step_data["source"], 
                "destination": step_data["destination"]
            },
            "conditions": {},
            "error_handling": "stop"
        }
    
    elif raw_type == "input":
        return {
            "step_type": "input",
            "params": {
                "prompt": step_data["prompt"],
                "default": step_data.get("default"),
                "variable_name": step_data.get("variable_name", "user_input")
            },
            "conditions": {},
            "error_handling": "stop"
        }
    
    else:
        # Unknown step type - create generic step
        return {
            "step_type": "unknown",
            "params": step_data,
            "conditions": {},
            "error_handling": "continue"  # Don't stop on unknown steps
        }
```

#### **JSON and Requirements.txt Parsers**

```python
def parse_json(self, file_path: str) -> List[Dict[str, Any]]:
    """
    IMPLEMENTATION PLAN: Direct JSON to standardized format conversion
    
    Pinokio JSON format is already structured, so this is straightforward
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # JSON format is typically an array of step objects
    standardized_recipe = []
    
    if isinstance(json_data, list):
        for step in json_data:
            standardized_step = self._convert_json_step(step)
            if standardized_step:
                standardized_recipe.append(standardized_step)
    elif isinstance(json_data, dict):
        # Single step JSON file
        standardized_step = self._convert_json_step(json_data)
        if standardized_step:
            standardized_recipe.append(standardized_step)
    
    return standardized_recipe

def parse_requirements(self, file_path: str) -> List[Dict[str, Any]]:
    """
    IMPLEMENTATION PLAN: Convert requirements.txt to pip install steps
    """
    standardized_recipe = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Convert each requirement to a pip install step
            standardized_recipe.append({
                "step_type": "shell_run",
                "params": {
                    "command": f"pip install {line}",
                    "args": [],
                    "options": {}
                },
                "conditions": {},
                "error_handling": "stop"
            })
    
    return standardized_recipe
```

---

## **3. `app/core/P05_SearchEngine.py` - Application Discovery Intelligence**

### **Core Architecture Overview**
This module provides fast, weighted search across the Pinokio applications database with support for text queries, category filters, and tag filters. The design prioritizes search speed and relevance ranking.

### **In-Memory Data Structure Decision**

**Choice**: **List of Dataclasses** over Pandas DataFrame

**Justification:**
```python
@dataclass
class PinokioApp:
    """
    IMPLEMENTATION PLAN: Structured app data for efficient searching
    
    WHY DATACLASS OVER PANDAS:
    1. Lower memory overhead for < 10,000 apps
    2. Better type safety and IDE support  
    3. No Pandas dependency (lighter deployment)
    4. Native Python performance for filtering
    5. Easier serialization and debugging
    """
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    author: str
    install_size_mb: Optional[int]
    gpu_required: bool
    install_url: str
    thumbnail_url: Optional[str]
    
    # Pre-computed search fields for performance
    search_text: str = field(init=False)  # Concatenated searchable text
    tag_set: Set[str] = field(init=False)  # Tags as set for O(1) lookup
    
    def __post_init__(self):
        # Pre-compute search text (lowercase for case-insensitive search)
        self.search_text = f"{self.name} {self.description} {' '.join(self.tags)}".lower()
        
        # Convert tags to set for efficient membership testing
        self.tag_set = set(tag.lower() for tag in self.tags)
```

### **Method Implementation Plans**

#### **`load_apps_database(self) -> bool`**

**Database Loading Strategy:**
```python
def load_apps_database(self) -> bool:
    """
    IMPLEMENTATION PLAN:
    
    1. Load cleaned_pinokio_apps.json
    2. Convert to PinokioApp dataclasses
    3. Build search indices for performance
    4. Handle malformed data gracefully
    """
    
    try:
        # Load JSON data
        apps_file_path = Path("data/cleaned_pinokio_apps.json")
        with open(apps_file_path, 'r', encoding='utf-8') as f:
            raw_apps_data = json.load(f)
        
        # Convert to dataclasses
        self.apps: List[PinokioApp] = []
        
        for app_data in raw_apps_data:
            try:
                app = PinokioApp(
                    id=app_data.get('id', ''),
                    name=app_data.get('name', 'Unknown'),
                    description=app_data.get('description', ''),
                    category=app_data.get('category', 'Other'),
                    tags=app_data.get('tags', []),
                    author=app_data.get('author', 'Unknown'),
                    install_size_mb=app_data.get('install_size_mb'),
                    gpu_required=app_data.get('gpu_required', False),
                    install_url=app_data.get('install_url', ''),
                    thumbnail_url=app_data.get('thumbnail_url')
                )
                self.apps.append(app)
                
            except Exception as e:
                # Log malformed app data but continue loading
                print(f"Warning: Skipped malformed app data: {e}")
                continue
        
        # Build search indices
        self._build_search_indices()
        
        print(f"Loaded {len(self.apps)} applications successfully")
        return True
        
    except Exception as e:
        print(f"Failed to load apps database: {e}")
        return False

def _build_search_indices(self):
    """
    IMPLEMENTATION PLAN: Pre-compute search indices for performance
    """
    # Category index for O(1) filtering
    self.category_index: Dict[str, List[PinokioApp]] = {}
    for app in self.apps:
        category = app.category.lower()
        if category not in self.category_index:
            self.category_index[category] = []
        self.category_index[category].append(app)
    
    # Tag index for O(1) tag filtering  
    self.tag_index: Dict[str, List[PinokioApp]] = {}
    for app in self.apps:
        for tag in app.tags:
            tag_lower = tag.lower()
            if tag_lower not in self.tag_index:
                self.tag_index[tag_lower] = []
            self.tag_index[tag_lower].append(app)
```

#### **`_calculate_score(app: Dict[str, Any], query: str) -> float` - Weighted Relevance Algorithm**

**Scoring Strategy:**
```python
def _calculate_score(self, app: PinokioApp, query: str) -> float:
    """
    IMPLEMENTATION PLAN: Weighted relevance scoring algorithm
    
    SCORING WEIGHTS (based on search relevance priority):
    - Exact name match: 100 points
    - Name contains query: 50 points  
    - Tag exact match: 30 points per tag
    - Description contains query: 10 points per occurrence
    - Author contains query: 5 points
    
    ADDITIONAL MODIFIERS:
    - GPU apps get +5 bonus if system has GPU
    - Recently popular apps get small boost
    """
    
    if not query or not query.strip():
        return 0.0
    
    query_lower = query.lower().strip()
    score = 0.0
    
    # Name scoring (highest weight)
    name_lower = app.name.lower()
    if name_lower == query_lower:
        score += 100.0  # Exact match
    elif query_lower in name_lower:
        # Partial match with position bonus (earlier = better)
        position = name_lower.find(query_lower) 
        position_bonus = max(0, 20 - position)  # Up to 20 bonus points
        score += 50.0 + position_bonus
    
    # Tag scoring (high weight)
    for tag in app.tags:
        tag_lower = tag.lower()
        if tag_lower == query_lower:
            score += 30.0  # Exact tag match
        elif query_lower in tag_lower:
            score += 15.0  # Partial tag match
    
    # Description scoring (medium weight)
    description_lower = app.description.lower()
    occurrence_count = description_lower.count(query_lower)
    score += occurrence_count * 10.0
    
    # Author scoring (low weight)
    author_lower = app.author.lower()
    if query_lower in author_lower:
        score += 5.0
    
    # Modifiers
    # GPU bonus (encourage GPU apps on GPU systems)
    if app.gpu_required and self._system_has_gpu():
        score += 5.0
    
    # Category relevance bonus
    if self._is_trending_category(app.category):
        score += 2.0
    
    return score

def _system_has_gpu(self) -> bool:
    """Check if system has GPU (simplified implementation)"""
    try:
        import GPUtil
        return len(GPUtil.getGPUs()) > 0
    except ImportError:
        # Fallback: check NVIDIA-SMI
        import subprocess
        try:
            subprocess.run(['nvidia-smi'], capture_output=True, check=True)
            return True
        except:
            return False

def _is_trending_category(self, category: str) -> bool:
    """Simple trending category detection"""
    trending_categories = {'ai-art', 'chatbot', 'image-generation', 'text-generation'}
    return category.lower() in trending_categories
```

#### **`search(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`**

**Comprehensive Search Algorithm:**
```python
def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    IMPLEMENTATION PLAN: Complete search pipeline with filtering and ranking
    
    Pipeline Steps:
    1. Apply filters to reduce search space
    2. Calculate relevance scores for remaining apps
    3. Sort by score (descending)
    4. Return top results with metadata
    """
    
    if not self.apps:
        return []
    
    # Step 1: Apply filters to get candidate apps
    candidate_apps = self.apps.copy()  # Start with all apps
    
    if filters:
        # Category filter
        if 'category' in filters and filters['category']:
            candidate_apps = self._filter_by_category(candidate_apps, filters['category'])
        
        # Tags filter  
        if 'tags' in filters and filters['tags']:
            candidate_apps = self._filter_by_tags(candidate_apps, filters['tags'])
        
        # GPU filter
        if 'gpu_required' in filters:
            gpu_required = filters['gpu_required']
            candidate_apps = [app for app in candidate_apps if app.gpu_required == gpu_required]
        
        # Size filter (max install size)
        if 'max_size_mb' in filters and filters['max_size_mb']:
            max_size = filters['max_size_mb']
            candidate_apps = [
                app for app in candidate_apps 
                if app.install_size_mb is None or app.install_size_mb <= max_size
            ]
    
    # Step 2: Score and rank results
    scored_results = []
    
    for app in candidate_apps:
        score = self._calculate_score(app, query) if query else 1.0  # Default score for no query
        
        if score > 0:  # Only include apps with positive scores
            result = {
                'id': app.id,
                'name': app.name,
                'description': app.description,
                'category': app.category,
                'tags': app.tags,
                'author': app.author,
                'install_size_mb': app.install_size_mb,
                'gpu_required': app.gpu_required,
                'install_url': app.install_url,
                'thumbnail_url': app.thumbnail_url,
                'relevance_score': score
            }
            scored_results.append(result)
    
    # Step 3: Sort by relevance score (descending)
    scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Step 4: Limit results for performance (top 50)
    return scored_results[:50]

def _filter_by_category(self, apps: List[PinokioApp], category: str) -> List[PinokioApp]:
    """
    IMPLEMENTATION PLAN: Efficient category filtering using pre-built index
    """
    category_lower = category.lower()
    
    # Use pre-built index for O(1) lookup
    if category_lower in self.category_index:
        return self.category_index[category_lower].copy()
    else:
        return []  # No apps in this category

def _filter_by_tags(self, apps: List[PinokioApp], tags: List[str]) -> List[PinokioApp]:
    """
    IMPLEMENTATION PLAN: Tag filtering with AND/OR logic
    
    Default behavior: OR logic (app matches ANY of the specified tags)
    Could be extended to support AND logic via filter options
    """
    if not tags:
        return apps
    
    tags_lower = [tag.lower() for tag in tags]
    matching_apps = set()
    
    # Use tag index for efficient lookup
    for tag in tags_lower:
        if tag in self.tag_index:
            matching_apps.update(self.tag_index[tag])
    
    # Return intersection with input apps (preserves other filters)
    return [app for app in apps if app in matching_apps]
```

### **Performance Optimizations**

```python
# Additional performance considerations:

1. **Caching Strategy**:
   - Cache search results for repeated identical queries
   - Use LRU cache with 100-entry limit
   - Clear cache when database is reloaded

2. **Memory Management**:
   - Use __slots__ in PinokioApp dataclass to reduce memory
   - Lazy loading of thumbnail data
   - Periodic cleanup of unused cached data

3. **Search Optimizations**:
   - Pre-tokenize common search terms
   - Use fuzzy matching for typo tolerance (optional)
   - Implement pagination for large result sets

4. **Index Maintenance**:
   - Rebuild indices only when database changes
   - Incremental index updates for single app additions
   - Background index optimization during idle time
```

---

## **IMPLEMENTATION READINESS SUMMARY**

These blueprints provide comprehensive, implementable specifications for the three most complex Stage 1 modules:

✅ **P02_ProcessManager**: Complete async architecture with thread-safe PID management and real-time streaming  
✅ **P03_Translator**: Regex-based JavaScript parser with standardized recipe output format  
✅ **P05_SearchEngine**: Weighted search algorithm with efficient filtering and relevance ranking  

Each blueprint includes detailed pseudo-code, data structures, error handling strategies, and performance considerations. A junior developer can follow these specifications to produce production-ready code that adheres to all project requirements and architectural principles.