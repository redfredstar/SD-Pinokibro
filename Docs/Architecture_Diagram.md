# Architecture Diagram: PinokioCloud Centralized UI Orchestrator

## **System Overview**

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[launcher.ipynb - Jupyter UI]
        T1[Discover Tab]
        T2[My Library Tab]
        T3[Active Tunnels Tab]
        T4[Terminal Tab]
    end

    subgraph "Orchestration Layer"
        JQ[Job Queue<br/>queue.Queue]
        WT[Worker Thread<br/>_job_worker()]
        RF[Master Refresh<br/>refresh_ui()]
    end

    subgraph "Core Engine Layer"
        SM[StateManager<br/>SQLite Database]
        LM[LaunchManager<br/>App Execution]
        IM[InstallManager<br/>Installation Workflows]
        TM[TunnelManager<br/>pyngrok Integration]
        LibM[LibraryManager<br/>Certification & Cleanup]
    end

    subgraph "Utility Layer"
        WUD[WebUIDetector<br/>URL Extraction]
        SE[SearchEngine<br/>App Discovery]
        EM[EnvironmentManager<br/>Conda/venv Management]
        PM[ProcessManager<br/>Command Execution]
    end

    %% User Interactions
    UI --> JQ
    T1 --> JQ
    T2 --> JQ
    T3 --> JQ
    T4 --> JQ

    %% Job Processing
    JQ --> WT
    WT --> RF

    %% State Management
    RF --> SM
    SM --> RF

    %% Engine Integration
    WT --> LM
    WT --> IM
    WT --> TM
    WT --> LibM

    %% Utility Services
    LM --> WUD
    IM --> EM
    IM --> PM
    TM --> SM
    LibM --> SM

    %% UI Updates
    RF --> T1
    RF --> T2
    RF --> T3
    RF --> T4

    %% Styling
    classDef uiLayer fill:#e1f5fe
    classDef orchLayer fill:#f3e5f5
    classDef coreLayer fill:#e8f5e8
    classDef utilLayer fill:#fff3e0

    class UI,T1,T2,T3,T4 uiLayer
    class JQ,WT,RF orchLayer
    class SM,LM,IM,TM,LibM coreLayer
    class WUD,SE,EM,PM utilLayer
```

## **Architecture Principles**

### **Centralized Control**
- **Single Job Queue**: All user actions are serialized through `queue.Queue`
- **Persistent Worker**: One daemon thread processes all jobs sequentially
- **Master Refresh**: Single `refresh_ui()` function updates entire interface

### **State Management**
- **Database First**: SQLite database as single source of truth
- **Thread Safety**: All operations use proper locking mechanisms
- **Real-time Sync**: UI reflects database state immediately

### **Error Handling**
- **Comprehensive Boundaries**: Worker thread catches all exceptions
- **Full Tracebacks**: Complete error information provided to users
- **Graceful Degradation**: System remains stable after failures

### **Scalability**
- **Modular Design**: Each manager has single responsibility
- **Loose Coupling**: Components communicate through defined interfaces
- **Extension Points**: Architecture supports future enhancements