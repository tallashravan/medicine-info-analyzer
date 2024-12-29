import streamlit as st
from PIL import Image
import io
from agent_setup import load_environment_variables, initialize_agent
from utils import sanitize_input, save_feedback
import os

# Load Environment Variables
try:
    load_environment_variables()
except EnvironmentError as e:
    st.error(str(e))
    st.stop()

# Initialize Tavily Agent
try:
    tavily_agent = initialize_agent()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Medicine Analyzer",
    page_icon="💊",
    layout="wide",
)

# App Title and Description
st.title("💊 AI Medicine Analyzer")
st.header("Simplifying Medicine Insights with AI")
st.write(
    "Upload an image of your medicine label or prescription to get started. 📸 Want to see it in action? Explore Example Images for a quick demo! 🖼️ Curious to know more? Check out the About tab for details. ℹ️"
)

# Tabs for Main Upload, Example Images, and About
tab1, tab2, tab3, tab4 = st.tabs(["Upload Image", "Example Images", "About", "Feedback"])

### --- TAB 1: UPLOAD IMAGE ---
with tab1:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Upload a Medicine or Prescription Image", type=["png", "jpg", "jpeg"])

    def analyze_medicine(image_bytes):
        temp_image_path = "temp_image.jpg"
        try:
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)

            response = tavily_agent.run(
                "Analyze the medicine composition image",
                images=[temp_image_path]
            )
            return response.content
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return "Error: An unexpected error occurred."
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.image(uploaded_file, caption="Uploaded Image", width=300)
            image_bytes = io.BytesIO()
            image = image.convert('RGB')
            image.save(image_bytes, format='JPEG')
            image_bytes = image_bytes.getvalue()
        except Exception as e:
            st.error(f"Failed to process the uploaded image: {str(e)}")
            st.stop()

        if st.button("Analyze Uploaded Image"):
            if image_bytes:
                with st.spinner("Analyzing... Please wait."):
                    result = analyze_medicine(image_bytes)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        with st.expander("Analysis Results", expanded=True):
                            st.success("Analysis Complete! Here are the details:")
                            st.markdown(result)
            else:
                st.error("Failed to process the uploaded image. Please try again.")
    else:
        st.info(
            """
            **Upload an image of the medicine label to get started. 📸**  
            - Want to see it in action? Explore **Example Images** for a quick demo! 🖼️  
            - Curious to know more? Check out the **About** tab for details. ℹ️  
            """
        )
    st.warning("💡 **Disclaimer:** This analysis provided by the AI is for informational purposes only and is not intended as medical advice. Always consult a qualified healthcare professional for medical guidance.")

### --- TAB 2: EXAMPLE IMAGES ---
with tab2:
    st.header("Example Images")
    example_images = {
        "Example 1": "images/benadryl-1.jpeg",
        "Example 2": "images/dolo-1.jpeg",
    }

    cols = st.columns(2,border=True)

    for idx, (label, image_path) in enumerate(example_images.items()):
        with cols[idx % 2]:
            st.image(image_path, caption=label, width=300)
            if st.button(f"Analyze {label}"):
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                with st.spinner("Analyzing... Please wait."):
                    result = analyze_medicine(image_bytes)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        with st.expander(f"Analysis Results for {label}", expanded=True):
                            st.success("Analysis Complete! Here are the details:")
                            st.markdown(result)
    st.warning("💡 **Disclaimer:** This analysis provided by the AI is for informational purposes only and is not intended as medical advice. Always consult a qualified healthcare professional for medical guidance.")

### --- TAB 3: ABOUT ---
with tab3:
    st.header("About the AI Medicine Analyzer")
    st.write("""
**AI Medicine Analyzer** is a user-friendly tool that helps you easily understand the medicines you take by analyzing their labels.  
• Get clear details on the uses, benefits, side effects, and safety tips.  
• Explanations are simplified, making it easy for everyone to understand, even kids! 👶  
• Simply upload a medicine label or prescription to get started.
""")

### --- TAB 4: FEEDBACK ---
with tab4:
    st.header("💬 Share Your Feedback")
    st.write("We'd love to hear your thoughts about the app! 😊")

    with st.form(key="feedback_form"):
        name = st.text_input("Name (Optional):", max_chars=50)
        feedback = st.text_area("Your Feedback:", max_chars=200)
        rating = st.slider("Rate your experience (1 - Poor, 5 - Excellent):", 1, 5, 3)
        submit_button = st.form_submit_button(label="Submit Feedback")

        if submit_button:
            sanitized_feedback = sanitize_input(feedback)
            sanitized_name = sanitize_input(name)

            if not sanitized_feedback:
                st.warning("⚠️ Feedback cannot be empty. Please share your thoughts!")
            else:
                save_feedback(sanitized_name, sanitized_feedback, rating)
                st.success("🎉 Thank you for your feedback! 🙌")

### --- SUPPORT SECTION ---
st.markdown("---")
st.markdown(
    """
    ### 🌟 Liked the app?  
    Support this project by **giving it a star⭐ on GitHub**!  👉 https://github.com/tallashravan/medicine-info-analyzer  
    """
)
st.markdown("---")
st.markdown(
    """
    ### 🚀 Want to see more projects like this?  
    **Follow me on GitHub** to stay updated on my latest projects! 👉 https://github.com/tallashravan/
    """
)
st.markdown("---")
st.write("Made with ❤️ by [Shravan](https://github.com/tallashravan/)")