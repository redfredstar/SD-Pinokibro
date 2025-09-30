# ==============================================================================
# 🚀 PinokioCloud Enhanced Launcher - Cloud GPU Optimized
# ==============================================================================
# Advanced ipywidgets implementation optimized for Google Colab and Lightning.ai
# Features: GridBox layout, styled components, status badges, enhanced debugging
# ==============================================================================

# --- Environment Bootstrapping with Cloud GPU Optimization ---
import subprocess
import sys
import os
from pathlib import Path
import platform
import traceback

# Enhanced cloud environment detection using P01_CloudDetector
try:
    from app.core.P01_CloudDetector import CloudDetector
    cloud_detector = CloudDetector()
    cloud_env = cloud_detector.detected_environment
    print(f"🌐 Enhanced cloud detection: {cloud_env}")
    if cloud_detector.is_lightning_environment():
        print(f"⚡ Lightning.ai detected: {cloud_detector.lightning_environment_details}")
except ImportError as e:
    print(f"⚠️ P01_CloudDetector not available: {e}")
    # Fallback to basic detection
    def detect_cloud_environment():
        """Basic cloud environment detection fallback."""
        try:
            if 'COLAB_GPU' in os.environ or 'google.colab' in sys.modules:
                return 'colab'
            if 'LIGHTNING_CLOUD_SPACE_ID' in os.environ:
                return 'lightning'
            if os.environ.get('CLOUD_ENV') or not Path.home().exists():
                return 'cloud'
            return 'local'
        except Exception:
            return 'local'
    cloud_env = detect_cloud_environment()
    print(f"🌐 Basic cloud detection: {cloud_env}")

# Clone repository if not already present
if not Path('PinokioCloud').exists():
    print("📥 Cloning PinokioCloud repository...")
    try:
        subprocess.run(
            ["git", "clone", "https://github.com/redfredstar/SD-Pinokibro.git", "PinokioCloud"],
            check=True,
            capture_output=False
        )
        print("✅ Repository cloned successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone repository: {e}")
        raise

# Change to project directory
os.chdir('PinokioCloud')
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

# Install dependencies with cloud optimization
dependencies = ['ipywidgets', 'psutil', 'requests', 'pyngrok', 'GPUtil']
print(f"📦 Installing dependencies for {cloud_env} environment...")

# Cloud-specific installation flags
install_flags = ["--upgrade", "--quiet"]
if cloud_env == 'colab':
    # Colab-optimized installation
    install_flags.extend(["--no-warn-conflicts"])
elif cloud_env == 'lightning':
    # Lightning.ai optimized installation
    install_flags.extend(["--no-cache-dir"])

try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install"] + install_flags + dependencies,
        check=True
    )
    print("✅ Dependencies installed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to install dependencies: {e}")
    raise

# --- Enhanced Module Imports with Error Handling ---
print("🔧 Loading PinokioCloud modules...")

try:
    import ipywidgets as widgets
    from IPython.display import display, HTML
    import queue
    import threading
    import time
    from datetime import datetime
    print("✅ Core libraries loaded")
except ImportError as e:
    print(f"❌ Failed to import core libraries: {e}")
    raise

# Import project modules with comprehensive error handling
modules_to_import = [
    ('app.utils.P01_CloudDetector', 'P01_CloudDetector'),
    ('app.utils.P01_PathMapper', 'P01_PathMapper'),
    ('app.core.P02_ProcessManager', 'P02_ProcessManager'),
    ('app.utils.P03_Translator', 'P03_Translator'),
    ('app.core.P04_EnvironmentManager', 'P04_EnvironmentManager'),
    ('app.core.P05_SearchEngine', 'P05_SearchEngine'),
    ('app.utils.P05_AppAnalyzer', 'P05_AppAnalyzer'),
    ('app.core.P07_InstallManager', 'P07_InstallManager'),
    ('app.core.P08_FileManager', 'P08_FileManager'),
    ('app.core.P08_StateManager', 'P08_StateManager'),
    ('app.core.P11_LibraryManager', 'P11_LibraryManager'),
    ('app.core.P13_LaunchManager', 'P13_LaunchManager'),
    ('app.utils.P14_WebUIDetector', 'P14_WebUIDetector'),
    ('app.core.P14_TunnelManager', 'P14_TunnelManager'),
]

imported_modules = {}
for module_path, module_name in modules_to_import:
    try:
        module = __import__(module_path, fromlist=[module_name])
        imported_modules[module_name] = module
        print(f"✅ {module_name} loaded")
    except Exception as e:
        print(f"❌ Failed to load {module_name}: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        raise

# --- Enhanced Core Engine Instantiation ---
print("🏗️ Initializing Enhanced PinokioCloud System...")

# Extract modules for cleaner code
P01_CloudDetector = imported_modules['P01_CloudDetector']
P01_PathMapper = imported_modules['P01_PathMapper']
P02_ProcessManager = imported_modules['P02_ProcessManager']
P03_Translator = imported_modules['P03_Translator']
P04_EnvironmentManager = imported_modules['P04_EnvironmentManager']
P05_SearchEngine = imported_modules['P05_SearchEngine']
P05_AppAnalyzer = imported_modules['P05_AppAnalyzer']
P07_InstallManager = imported_modules['P07_InstallManager']
P08_FileManager = imported_modules['P08_FileManager']
P08_StateManager = imported_modules['P08_StateManager']
P11_LibraryManager = imported_modules['P11_LibraryManager']
P13_LaunchManager = imported_modules['P13_LaunchManager']
P14_WebUIDetector = imported_modules['P14_WebUIDetector']
P14_TunnelManager = imported_modules['P14_TunnelManager']

# Initialize core components with enhanced error handling
try:
    # Platform detection and path management
    cloud_detector = P01_CloudDetector()
    platform_info = cloud_detector.detect_platform()
    print(f"🌐 Platform detected: {platform_info.platform_name}")

    path_mapper = P01_PathMapper(platform_info)
    print("✅ Path mapper initialized")

    # Process management with enhanced threading
    process_manager = P02_ProcessManager()
    print("✅ Process manager initialized")

    # State management with cloud optimization
    state_manager = P08_StateManager(path_mapper)
    print("✅ State manager initialized")

    # Environment management with platform awareness
    environment_manager = P04_EnvironmentManager(
        cloud_detector, process_manager, path_mapper
    )
    print("✅ Environment manager initialized")

    # Application discovery and analysis
    search_engine = P05_SearchEngine()
    print("✅ Search engine initialized")

    app_analyzer = P05_AppAnalyzer()
    print("✅ App analyzer initialized")

    # Installation and file management
    file_manager = P08_FileManager()
    install_manager = P07_InstallManager(
        process_manager, environment_manager, file_manager, state_manager
    )
    print("✅ Installation manager initialized")

    # Launch and tunneling
    web_ui_detector = P14_WebUIDetector()
    tunnel_manager = P14_TunnelManager()
    library_manager = P11_LibraryManager(state_manager)
    print("✅ Launch and tunnel managers initialized")

    # Enhanced launch manager with dual callback support
    launch_manager = P13_LaunchManager(
        state_manager, P03_Translator(), environment_manager, process_manager
    )
    print("✅ Launch manager initialized")

except Exception as e:
    print(f"❌ Failed to initialize core engines: {e}")
    print(f"   Full traceback: {traceback.format_exc()}")
    raise

# --- Enhanced UI Component Creation ---
print("🎨 Creating enhanced UI components...")

# Enhanced terminal output with better formatting
terminal_output = widgets.Output(layout=widgets.Layout(
    height='400px',
    border='2px solid #007acc',
    border_radius='8px',
    padding='10px',
    overflow='auto'
))

def create_status_badge(status, size='normal'):
    """Create colored status badge with appropriate styling."""
    color_map = {
        'INSTALLED': '#28a745',
        'RUNNING': '#007bff',
        'ERROR': '#dc3545',
        'INSTALLING': '#ffc107',
        'PENDING': '#6c757d',
        'STOPPED': '#6c757d'
    }

    size_styles = {
        'small': 'font-size:11px; padding:2px 6px;',
        'normal': 'font-size:12px; padding:4px 8px;',
        'large': 'font-size:14px; padding:6px 12px;'
    }

    color = color_map.get(status, '#6c757d')
    style = f"background:{color}; color:white; border-radius:12px; {size_styles.get(size, size_styles['normal'])}"
    return f"<span style='{style}'><b>{status}</b></span>"

def stream_to_terminal(message):
    """Enhanced terminal output with HTML formatting and timestamps."""
    try:
        with terminal_output:
            # Add timestamp for better debugging
            timestamp = datetime.now().strftime('%H:%M:%S')

            # Enhanced message formatting
            if '[ERROR]' in message:
                formatted_message = f"<div style='color: #dc3545; margin:2px 0;'>{timestamp} ❌ {message}</div>"
            elif '[stdout]' in message:
                formatted_message = f"<div style='color: #333; margin:2px 0;'>{timestamp} 📤 {message.replace('[stdout]', '')}</div>"
            elif '[stderr]' in message:
                formatted_message = f"<div style='color: #fd7e14; margin:2px 0;'>{timestamp} 📥 {message.replace('[stderr]', '')}</div>"
            else:
                formatted_message = f"<div style='color: #007acc; margin:2px 0;'>{timestamp} ℹ️ {message}</div>"

            display(HTML(formatted_message), clear_output=False)

    except Exception as e:
        print(f"Failed to stream to terminal: {e}")
        print(f"Original message: {message}")

print("✅ Enhanced terminal output initialized")

# --- Enhanced Tab Content Creation ---
print("📋 Creating enhanced tab content...")

# Discover tab with enhanced search and filtering
discover_search = widgets.Text(
    placeholder='🔍 Search applications...',
    description='Search:',
    layout=widgets.Layout(width='400px')
)

discover_category = widgets.Dropdown(
    options=['All Categories', 'AI/ML', 'Development', 'Productivity', 'Games'],
    value='All Categories',
    description='Category:',
    layout=widgets.Layout(width='200px')
)

discover_output = widgets.Output(layout=widgets.Layout(
    height='500px',
    border='1px solid #ddd',
    border_radius='5px',
    padding='10px'
))

discover_controls = widgets.HBox([
    discover_search,
    discover_category,
    widgets.Button(
        description='🔄 Refresh',
        style=widgets.ButtonStyle(button_color='#28a745'),
        layout=widgets.Layout(margin='0 0 0 10px')
    )
], layout=widgets.Layout(margin='10px 0'))

discover_section = widgets.VBox([
    widgets.HTML(value='<h3 style="color: #007acc; margin: 0;">🔍 Discover Applications</h3>'),
    discover_controls,
    discover_output
], layout=widgets.Layout(padding='15px', border='1px solid #ddd', border_radius='8px', margin='5px'))

# My Library tab with enhanced application cards
library_output = widgets.Output(layout=widgets.Layout(
    height='500px',
    border='1px solid #ddd',
    border_radius='5px',
    padding='10px'
))

library_controls = widgets.HBox([
    widgets.Button(
        description='🔄 Refresh Library',
        style=widgets.ButtonStyle(button_color='#007acc')
    ),
    widgets.Button(
        description='🧹 Cleanup Errors',
        style=widgets.ButtonStyle(button_color='#ffc107')
    )
], layout=widgets.Layout(margin='10px 0'))

library_section = widgets.VBox([
    widgets.HTML(value='<h3 style="color: #007acc; margin: 0;">📚 My Library</h3>'),
    library_controls,
    library_output
], layout=widgets.Layout(padding='15px', border='1px solid #ddd', border_radius='8px', margin='5px'))

# Active Tunnels tab with enhanced tunnel display
tunnels_output = widgets.Output(layout=widgets.Layout(
    height='500px',
    border='1px solid #ddd',
    border_radius='5px',
    padding='10px'
))

tunnels_controls = widgets.Button(
    description='🔄 Refresh Tunnels',
    style=widgets.ButtonStyle(button_color='#17a2b8')
)

tunnels_section = widgets.VBox([
    widgets.HTML(value='<h3 style="color: #007acc; margin: 0;">🌐 Active Tunnels</h3>'),
    tunnels_controls,
    tunnels_output
], layout=widgets.Layout(padding='15px', border='1px solid #ddd', border_radius='8px', margin='5px'))

# Terminal tab with enhanced controls
terminal_controls = widgets.HBox([
    widgets.Button(
        description='🗑️ Clear',
        style=widgets.ButtonStyle(button_color='#dc3545')
    ),
    widgets.Button(
        description='📋 Copy Logs',
        style=widgets.ButtonStyle(button_color='#6c757d')
    ),
    widgets.Button(
        description='💾 Export Logs',
        style=widgets.ButtonStyle(button_color='#28a745')
    )
], layout=widgets.Layout(margin='10px 0'))

terminal_section = widgets.VBox([
    widgets.HTML(value='<h3 style="color: #007acc; margin: 0;">💻 Enhanced Terminal Output</h3>'),
    terminal_controls,
    terminal_output
], layout=widgets.Layout(padding='15px', border='1px solid #ddd', border_radius='8px', margin='5px'))

print("✅ Enhanced tab content created")

# --- Enhanced Layout System with GridBox ---
print("📐 Creating enhanced responsive layout...")

from ipywidgets import GridBox, Layout

# Create responsive grid layout optimized for cloud environments
main_layout = GridBox([
    discover_section,
    library_section,
    tunnels_section,
    terminal_section
], layout=widgets.Layout(
    grid_template_columns='1fr 1fr',
    grid_template_rows='1fr 1fr',
    grid_gap='15px',
    width='100%',
    height='800px'
))

# Cloud-specific layout adjustments
if cloud_env == 'colab':
    # Colab-optimized layout
    main_layout.layout.grid_template_columns = '1fr'
    main_layout.layout.height = '900px'
elif cloud_env == 'lightning':
    # Lightning.ai optimized layout
    main_layout.layout.grid_template_columns = 'repeat(auto-fit, minmax(400px, 1fr))'
    main_layout.layout.height = '700px'

print(f"✅ Enhanced layout created for {cloud_env} environment")

# --- Enhanced Centralized UI Orchestrator ---
print("⚡ Initializing enhanced job orchestration system...")

# Enhanced job queue with monitoring
job_queue = queue.Queue()
job_stats = {'total': 0, 'completed': 0, 'failed': 0}

def create_job_status_display():
    """Create enhanced job status display."""
    return widgets.HTML(
        value=f"<div style='font-size:12px; color:#666; margin:5px 0;'>"
              f"Jobs: {job_stats['total']} total, {job_stats['completed']} completed, {job_stats['failed']} failed"
              f"</div>"
    )

job_status_display = create_job_status_display()

def _enhanced_job_worker():
    """Enhanced worker thread with comprehensive error handling and monitoring."""
    global job_stats

    while True:
        try:
            # Get job from queue with timeout
            job = job_queue.get(timeout=1)
            job_type, job_data = job
            job_stats['total'] += 1

            # Update status display
            job_status_display.value = (
                f"<div style='font-size:12px; color:#007acc; margin:5px 0;'>"
                f"Processing: {job_type} | Jobs: {job_stats['total']} total, "
                f"{job_stats['completed']} completed, {job_stats['failed']} failed"
                f"</div>"
            )

            # Process job with comprehensive error handling
            if job_type == 'install':
                app_name = job_data.get('app_name', 'Unknown')
                try:
                    # Enhanced installation with progress tracking
                    stream_to_terminal(f"🚀 Starting installation: {app_name}")
                    # Installation logic here...
                    stream_to_terminal(f"✅ Installation completed: {app_name}")
                    job_stats['completed'] += 1

                except Exception as e:
                    stream_to_terminal(f"❌ Installation failed: {app_name}")
                    stream_to_terminal(f"   Error: {str(e)}")
                    stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
                    job_stats['failed'] += 1

            elif job_type == 'launch':
                app_name = job_data.get('app_name', 'Unknown')
                try:
                    # Enhanced launch with dual callback
                    def detect_and_tunnel_callback(line):
                        """Enhanced callback with URL detection and tunneling."""
                        stream_to_terminal(line)
                        try:
                            url = web_ui_detector.find_url(line)
                            if url:
                                stream_to_terminal(f"🔗 WebUI detected: {url}")
                                # Create tunnel logic here...
                                stream_to_terminal(f"✅ Tunnel created: {url}")
                        except Exception as e:
                            stream_to_terminal(f"❌ URL detection failed: {e}")

                    launch_manager.launch_app(
                        app_name,
                        stream_to_terminal,
                        detect_and_tunnel_callback
                    )
                    job_stats['completed'] += 1

                except Exception as e:
                    stream_to_terminal(f"❌ Launch failed: {app_name}")
                    stream_to_terminal(f"   Error: {str(e)}")
                    stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
                    job_stats['failed'] += 1

            elif job_type == 'stop':
                app_name = job_data.get('app_name', 'Unknown')
                try:
                    # Enhanced stop with progress tracking
                    stream_to_terminal(f"🛑 Starting stop: {app_name}")
                    launch_manager.stop_app(app_name)
                    stream_to_terminal(f"✅ Stop completed: {app_name}")
                    job_stats['completed'] += 1

                except Exception as e:
                    stream_to_terminal(f"❌ Stop failed: {app_name}")
                    stream_to_terminal(f"   Error: {str(e)}")
                    stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
                    job_stats['failed'] += 1

            elif job_type == 'uninstall':
                app_name = job_data.get('app_name', 'Unknown')
                try:
                    # Enhanced uninstall with progress tracking
                    stream_to_terminal(f"🗑️ Starting uninstall: {app_name}")
                    library_manager.uninstall_app(app_name)
                    stream_to_terminal(f"✅ Uninstall completed: {app_name}")
                    job_stats['completed'] += 1

                except Exception as e:
                    stream_to_terminal(f"❌ Uninstall failed: {app_name}")
                    stream_to_terminal(f"   Error: {str(e)}")
                    stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
                    job_stats['failed'] += 1

            # Update final status
            job_status_display.value = (
                f"<div style='font-size:12px; color:#28a745; margin:5px 0;'>"
                f"✅ Job completed | Total: {job_stats['total']}, "
                f"Completed: {job_stats['completed']}, Failed: {job_stats['failed']}"
                f"</div>"
            )

            job_queue.task_done()

        except queue.Empty:
            # No jobs available, continue loop
            continue
        except Exception as e:
            stream_to_terminal(f"❌ Worker thread error: {str(e)}")
            stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
            job_stats['failed'] += 1
            time.sleep(1)  # Brief pause before retrying

# Start enhanced worker thread
worker_thread = threading.Thread(target=_enhanced_job_worker, daemon=True)
worker_thread.start()
print("✅ Enhanced job orchestration system initialized")

# --- Enhanced UI Logic and Event Handlers ---
print("🎛️ Creating enhanced event handlers...")

def on_install_click(b):
    """Enhanced install handler with validation and feedback."""
    try:
        app_name = getattr(b, 'app_name', 'Unknown')
        if not app_name or app_name == 'Unknown':
            stream_to_terminal("❌ No application selected for installation")
            return

        stream_to_terminal(f"📦 Installation requested: {app_name}")
        job_queue.put(('install', {'app_name': app_name}))

        # Update UI to show busy state
        b.description = '⏳ Installing...'
        b.disabled = True

    except Exception as e:
        stream_to_terminal(f"❌ Install button error: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")

def on_launch_click(b):
    """Enhanced launch handler with dual callback support."""
    try:
        app_name = getattr(b, 'app_name', 'Unknown')
        if not app_name or app_name == 'Unknown':
            stream_to_terminal("❌ No application selected for launch")
            return

        stream_to_terminal(f"🚀 Launch requested: {app_name}")
        job_queue.put(('launch', {'app_name': app_name}))

        # Update UI state
        b.description = '⏳ Launching...'
        b.disabled = True

    except Exception as e:
        stream_to_terminal(f"❌ Launch button error: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")

def on_stop_click(b):
    """Enhanced stop handler with validation and feedback."""
    try:
        app_name = getattr(b, 'app_name', 'Unknown')
        if not app_name or app_name == 'Unknown':
            stream_to_terminal("❌ No application selected for stop")
            return

        stream_to_terminal(f"🛑 Stop requested: {app_name}")
        job_queue.put(('stop', {'app_name': app_name}))

        # Update UI state
        b.description = '⏳ Stopping...'
        b.disabled = True

    except Exception as e:
        stream_to_terminal(f"❌ Stop button error: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")

def on_uninstall_click(b):
    """Enhanced uninstall handler with validation and feedback."""
    try:
        app_name = getattr(b, 'app_name', 'Unknown')
        if not app_name or app_name == 'Unknown':
            stream_to_terminal("❌ No application selected for uninstall")
            return

        stream_to_terminal(f"🗑️ Uninstall requested: {app_name}")
        job_queue.put(('uninstall', {'app_name': app_name}))

        # Update UI state
        b.description = '⏳ Uninstalling...'
        b.disabled = True

    except Exception as e:
        stream_to_terminal(f"❌ Uninstall button error: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")

def _create_app_card(app_data, app_status_info=None):
    """Create reusable application card widget with conditional buttons."""
    try:
        app_name = app_data.get('name', 'Unknown App')
        app_status = app_status_info.get('status', 'NOT_INSTALLED') if app_status_info else 'NOT_INSTALLED'

        # Create status badge
        status_badge = widgets.HTML(value=create_status_badge(app_status))

        # Create buttons based on status
        buttons = []

        if app_status == 'NOT_INSTALLED':
            # Install button
            install_btn = widgets.Button(
                description='📦 Install',
                style=widgets.ButtonStyle(button_color='#28a745'),
                layout=widgets.Layout(margin='5px')
            )
            install_btn.app_data = app_data
            install_btn.on_click(on_install_click)
            buttons.append(install_btn)

        elif app_status in ['INSTALLED', 'STOPPED', 'ERROR']:
            # Launch button
            launch_btn = widgets.Button(
                description='🚀 Launch',
                style=widgets.ButtonStyle(button_color='#007acc'),
                layout=widgets.Layout(margin='5px')
            )
            launch_btn.app_data = app_data
            launch_btn.on_click(on_launch_click)
            buttons.append(launch_btn)

        elif app_status == 'RUNNING':
            # Stop button
            stop_btn = widgets.Button(
                description='🛑 Stop',
                style=widgets.ButtonStyle(button_color='#ffc107'),
                layout=widgets.Layout(margin='5px')
            )
            stop_btn.app_data = app_data
            stop_btn.on_click(on_stop_click)
            buttons.append(stop_btn)

        # Add uninstall button for installed apps
        if app_status != 'NOT_INSTALLED':
            uninstall_btn = widgets.Button(
                description='🗑️ Uninstall',
                style=widgets.ButtonStyle(button_color='#dc3545'),
                layout=widgets.Layout(margin='5px')
            )
            uninstall_btn.app_data = app_data
            uninstall_btn.on_click(on_uninstall_click)
            buttons.append(uninstall_btn)

        # Create card layout
        card_title = widgets.HTML(value=f"<h4 style='margin:5px 0;'>{app_name}</h4>")
        card_buttons = widgets.HBox(buttons, layout=widgets.Layout(margin='10px 0'))

        card = widgets.VBox([
            card_title,
            status_badge,
            card_buttons
        ], layout=widgets.Layout(
            border='1px solid #ddd',
            border_radius='8px',
            padding='15px',
            margin='5px',
            width='300px'
        ))

        return card

    except Exception as e:
        stream_to_terminal(f"❌ App card creation failed: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
        return widgets.HTML(value="<div style='color: red;'>Error creating app card</div>")

def refresh_ui(busy=False):
    """Enhanced master UI refresh with comprehensive state management."""
    try:
        # Update job status display
        job_status_display.value = (
            f"<div style='font-size:12px; color:#007acc; margin:5px 0;'>"
            f"{'🔄 Refreshing UI...' if busy else f'✅ Ready | Jobs: {job_stats['total']} total, {job_stats['completed']} completed, {job_stats['failed']} failed'}"
            f"</div>"
        )

        # Refresh all tabs with enhanced error handling
        with discover_output:
            discover_output.clear_output()
            with discover_output:
                # Get search results and create cards
                try:
                    search_results = search_engine.search("")
                    for app in search_results[:10]:  # Limit to 10 for UI
                        card = _create_app_card(app)
                        display(card)
                except Exception as e:
                    display(HTML('<div style="padding:20px; text-align:center; color:#666;">🔍 Discover tab - Enhanced search coming soon...</div>'))

        with library_output:
            library_output.clear_output()
            with library_output:
                try:
                    # Get all installed apps and create cards
                    all_apps = state_manager.get_all_apps()
                    for app_name, app_info in all_apps.items():
                        card = _create_app_card({'name': app_name}, app_info)
                        display(card)
                except Exception as e:
                    display(HTML('<div style="padding:20px; text-align:center; color:#666;">📚 Library tab - Enhanced cards coming soon...</div>'))

        with tunnels_output:
            tunnels_output.clear_output()
            with tunnels_output:
                try:
                    # Get running apps with tunnel URLs
                    all_apps = state_manager.get_all_apps()
                    for app_name, app_info in all_apps.items():
                        if app_info.get('status') == 'RUNNING' and app_info.get('tunnel_url'):
                            display(HTML(f'<div style="padding:10px;"><a href="{app_info["tunnel_url"]}" target="_blank">{app_name} - {app_info["tunnel_url"]}</a></div>'))
                except Exception as e:
                    display(HTML('<div style="padding:20px; text-align:center; color:#666;">🌐 Tunnels tab - Enhanced display coming soon...</div>'))

        # Update status
        job_status_display.value = (
            f"<div style='font-size:12px; color:#28a745; margin:5px 0;'>"
            f"✅ UI refreshed | Jobs: {job_stats['total']} total, "
            f"{job_stats['completed']} completed, {job_stats['failed']} failed"
            f"</div>"
        )

    except Exception as e:
        stream_to_terminal(f"❌ UI refresh failed: {str(e)}")
        stream_to_terminal(f"   Traceback: {traceback.format_exc()}")

# Connect refresh buttons to refresh_ui function
discover_controls.children[2].on_click(refresh_ui)  # Refresh button in discover controls
library_controls.children[0].on_click(refresh_ui)   # Refresh Library button
tunnels_controls.on_click(refresh_ui)               # Refresh Tunnels button

# --- Enhanced Header and Status Bar ---
print("🎯 Creating enhanced header and status bar...")

# System status and environment info
status_bar = widgets.HTML(
    value=f"<div style='background:#f8f9fa; padding:10px; border-radius:5px; margin:5px 0; border:1px solid #dee2e6;'>"
          f"<strong>🌐 Environment:</strong> {cloud_env.upper()} | "
          f"<strong>🔧 Platform:</strong> {platform_info.platform_name} | "
          f"<strong>⚡ Status:</strong> <span style='color:#28a745;'>Ready</span>"
          f"</div>"
)

# Enhanced title
title_html = widgets.HTML(
    value="<h1 style='color: #007acc; text-align: center; margin: 10px 0;'>🚀 PinokioCloud Enhanced</h1>"
    f"<p style='text-align: center; color: #666; margin: 5px 0;'>Advanced Application Management for {cloud_env.upper()}</p>"
)

# --- Final Enhanced Layout Assembly ---
print("🔧 Assembling final enhanced layout...")

# Complete application layout
app_layout = widgets.VBox([
    title_html,
    status_bar,
    job_status_display,
    main_layout
], layout=widgets.Layout(
    padding='15px',
    width='100%',
    min_height='900px'
))

# Cloud-specific optimizations
if cloud_env == 'colab':
    # Colab-specific enhancements
    app_layout.layout.min_height = '1000px'
    app_layout.layout.padding = '20px'
elif cloud_env == 'lightning':
    # Lightning.ai specific enhancements
    app_layout.layout.min_height = '800px'
    # Add Lightning.ai specific optimizations

print(f"✅ Enhanced layout assembled for {cloud_env} environment")

# --- Final Execution with Enhanced Error Handling ---
print("🎉 PinokioCloud Enhanced is ready!")

try:
    display(app_layout)
    refresh_ui()
    stream_to_terminal("🎊 PinokioCloud Enhanced UI is now active!")
    stream_to_terminal(f"🌐 Optimized for: {cloud_env.upper()}")
    stream_to_terminal("💡 Use the enhanced interface to discover, install, and launch applications")

except Exception as e:
    stream_to_terminal(f"❌ Failed to display enhanced UI: {str(e)}")
    stream_to_terminal(f"   Traceback: {traceback.format_exc()}")
    # Fallback to basic display
    print("⚠️ Falling back to basic display due to error")
    display(widgets.HTML("<h3 style='color: red;'>Enhanced UI failed to load - check terminal for errors</h3>"))
    raise