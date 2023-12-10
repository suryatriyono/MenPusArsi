import streamlit as st
import function.myFunc as mf

def main():
    if "role" in st.session_state:
        if st.session_state["role"] == "1":
            mf.user()
        elif st.session_state["role"] == "9":
            mf.admin()
        else:
            del st.session_state['role']
            mf.login()
    else:
        mf.login()

            
if __name__ == "__main__":
    main()