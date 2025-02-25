import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.agent import AgentService

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent_service' not in st.session_state:
        st.session_state.agent_service = AgentService()
    if 'project_id' not in st.session_state:
        st.session_state.project_id = None
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = None

def main():
    st.set_page_config(page_title="CustomGPT Chat", layout="wide")
    initialize_session_state()

    st.title("CustomGPT Chat Interface")

    # Sidebar for project management
    with st.sidebar:
        st.header("Project Management")
        
        projects = st.session_state.agent_service.list_agents()

        selected_project = st.selectbox(
            "Select a project",
            options=[(p['id'], p['project_name']) for p in projects["data"]],
            format_func=lambda x: x[1]
        )

        if selected_project:
            st.session_state.project_id = selected_project[0]
        if projects["total"] == 0:
            st.info("No projects found. Please create a new project.")

        # Create new project
        # st.subheader("Create New Project")
        # project_name = st.text_input("Project Name")
        
        # if project_name and st.button("Create Project"):
        #     project_id = st.session_state.agent_service.create_agent(project_name)
        #     st.session_state.project_id = project_id
        #     st.success(f"Project created successfully! ID: {project_id}")

    # Main chat interface
    if st.session_state.project_id:
        # Create conversation if not exists
        if not st.session_state.conversation_id:
            st.session_state.conversation_id = st.session_state.agent_service.create_conversation(
                st.session_state.project_id
            )
        # st.session_state.conversation_id = "3698647"

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("What would you like to ask?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Handle streaming response
                for chunk in st.session_state.agent_service.chat_with_agent(
                    prompt,
                    st.session_state.project_id,
                    st.session_state.conversation_id,
                    stream=1
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.info("Please select or create a project to start chatting.")

if __name__ == "__main__":
    main()