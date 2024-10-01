import streamlit as st
import os

def get_pages():
    # This function can be cached if needed
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages_dir = os.path.join(script_dir, "page")
    pages = []
    for filename in os.listdir(pages_dir):
        if filename.endswith(".py"):
            page_name = filename[:-3].replace("_", " ").title()
            pages.append({
                "name": page_name,
                "label": page_name,
                "path": f"pages/{filename}"
            })
    return pages

def navigation_menu():
    pages = get_pages()
    
    st.sidebar.title("Navigation")
    for page in pages:
        if st.sidebar.button(page["label"], key=page["path"]):
            st.switch_page(page["path"])
