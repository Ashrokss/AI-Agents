# style.py
# Contains all CSS styling for the app

CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        font-weight: 500;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .research-card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .download-btn {
        display: inline-flex;
        align-items: center;
        background-color: #047857;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        margin-top: 10px;
    }
    .history-item {
        padding: 10px;
        border-bottom: 1px solid #E2E8F0;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #F1F5F9;
    }
    .agent-container {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 8px;
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
    }
    .agent-image {
        width: 60px;
        height: 60px;
        margin-right: 15px;
        object-fit: contain;
    }
    .agent-details {
        flex-grow: 1;
    }
    .agent-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .agent-status {
        font-size: 0.9rem;
        color: #4B5563;
    }
    .active-agent {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .completed-agent {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
    }
    .pending-agent {
        background-color: #F9FAFB;
        border-left: 4px solid #9CA3AF;
        opacity: 0.7;
    }
    .agent-progress {
        height: 6px;
        margin-top: 8px;
        border-radius: 3px;
        background-color: #E5E7EB;
        overflow: hidden;
    }
    .agent-progress-bar {
        height: 100%;
        background-color: #3B82F6;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    .completed-progress-bar {
        background-color: #10B981;
    }
</style>
"""