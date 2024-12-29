import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from phi.tools.tavily import TavilyTools
from prompts import INSTRUCTIONS, SYSTEM_PROMPT
import os
from PIL import Image
import io
import time

# Load Environment Variables
load_dotenv()

# Set API Keys
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize Tavily Agent
tavily_agent = Agent(
    name="tavily",
    instructions=INSTRUCTIONS,
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[TavilyTools()],
    markdown=True,
    system_prompt=SYSTEM_PROMPT
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Medicine Analyzer",
    page_icon="💊",
    layout="wide",
)

# Header Section
st.title("💊 AI Medicine Analyzer")
st.write("### Learn about your medicine in seconds! 🚀")

# Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["📂 Upload Image", "🖼️ Example Images", "ℹ️ About"])

# Function to Analyze Medicine
def analyze_medicine(image_bytes):
    temp_image_path = "temp_image.jpg"
    try:
        # Save Image Temporarily
        with open(temp_image_path, "wb") as f:
            f.write(image_bytes)

        # Analyze Image with Tavily Agent
        response = tavily_agent.run(
            "Analyze the medicine composition image",
            images=[temp_image_path]
        )

        return response.content

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "An error occurred while analyzing the image. Please try again later."
    finally:
        os.remove(temp_image_path)

# Tab 1 - Upload Image
with tab1:
    st.header("📂 Upload Medicine Label")
    uploaded_file = st.file_uploader("Upload a Medicine Label Image:", type=["png", "jpg", "jpeg"])

    # Show Uploaded Image
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        image = Image.open(uploaded_file)
        image_bytes = io.BytesIO()
        image = image.convert('RGB')
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()

        # Analyze Button
        if st.button("🔍 Analyze Now"):
            with st.spinner("Analyzing... Please wait."):
                # Progress Bar
                progress = st.progress(0)
                for percent in range(0, 101, 10):
                    time.sleep(0.1)
                    progress.progress(percent)
                result = analyze_medicine(image_bytes)

                # Show Results
                if result.startswith("Error"):
                    st.error(result)
                else:
                    with st.expander("📝 Analysis Results", expanded=True):
                        st.success("Analysis Complete! 🎉 Here are the details:")
                        st.markdown(result)

    else:
        st.info(
        """
        **Upload an image of the medicine label to get started. 📸**  
        - Want to see it in action? Explore **Example Images** for a quick demo! 🖼️  
        - Curious to know more? Check out the **About** tab for details. ℹ️  
        """
    )

# Tab 2 - Example Images
with tab2:
    st.header("🖼️ Example Images")
    st.write("Try analyzing these example medicine images:")

    example_images = {
        "Benadryl": "images/benadryl.jpeg",
        "Dolo 650": "images/dolo.jpeg",
    }

    cols = st.columns(2)
    for idx, (label, image_path) in enumerate(example_images.items()):
        with cols[idx % 2]:
            st.image(image_path, caption=label, width=300)
            if st.button(f"🔍 Analyze {label}"):
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                with st.spinner("Analyzing... Please wait."):
                    result = analyze_medicine(image_bytes)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        with st.expander(f"📊 Analysis Results for {label}", expanded=True):
                            st.success("Analysis Complete! 🎉")
                            st.markdown(result)

# Tab 3 - About Page
with tab3:
    st.header("ℹ️ About This App")
    st.write("""
    **AI Medicine Analyzer** is a simple and powerful AI tool designed to help you:
    - Understand medicine compositions quickly 📖
    - Learn their uses, benefits, and side effects ⚕️
    - Get important safety tips 🛡️

    **How It Works:**
    1. Upload a picture of a medicine label.
    2. AI analyzes the image and extracts useful information.
    3. Results are displayed instantly!

    🚀 *This is a proof of concept. We'd love your feedback!*  
    Made with ❤️ by [Shravan](https://github.com/tallashravan/)
    """)

# Footer and Disclaimer
st.markdown("---")
st.warning("💡 **Disclaimer:** This information is intended for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional for diagnosis and treatment.")