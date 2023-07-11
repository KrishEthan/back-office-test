import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


st.set_page_config(layout="wide")

def main():
    # Load config file
    st.session_state['authenticated'] = False
    with open("config.yaml", "r") as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        st.session_state['authenticated'] = True
        st.title("Home Page")
        authenticator.logout('Logout', 'main')
    elif authentication_status == False:
        st.session_state['authenticated'] = False
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
if __name__ == "__main__":
    main()
