import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from phi.tools.tavily import TavilyTools
from prompts import INSTRUCTIONS, SYSTEM_PROMPT
import os
from PIL import Image
import io

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
    page_title="Medicine Composition Analyzer",
    page_icon="💊",
    layout="wide",
)

# App Title and Description
st.title("💊 Medicine Info Analyzer")
st.write("Upload a picture of your medicine composition label to learn more about it— how it works, its uses, benefits, side effects, and safety tips.")

# Tabs for Main Upload and Example Images
tab1, tab2 = st.tabs(["Upload Image", "Example Images"])

with tab1:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Upload a Medicine Label Image", type=["png", "jpg", "jpeg"])

    def analyze_medicine(image_bytes):
        temp_image_path = "temp_image.jpg"
        try:
            # Save Image Temporarily
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)

            # Stream Handler
            result = []


            # Analyze Image with Tavily Agent
            response = tavily_agent.run(
                "Analyze the medicine composition image",
                images=[temp_image_path]
            )

            # Combine Stream Results
            # response = "".join(result)
            return response.content

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return "An error occurred while analyzing the image. Please try again later."
        finally:
            os.remove(temp_image_path)

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        image = Image.open(uploaded_file)
        image_bytes = io.BytesIO()
        image = image.convert('RGB')
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()

        if st.button("Analyze Uploaded Image"):
            with st.spinner("Analyzing... Please wait."):
                result = analyze_medicine(image_bytes)
                if result.startswith("Error"):
                    st.error(result)
                else:
                    with st.expander("Analysis Results", expanded=True):
                        st.success("Analysis Complete! Here are the details:")
                        st.markdown(result)
    else:
        with st.expander("ℹ️ How to Use This Tool?", expanded=True):
            st.write("Follow the steps below to analyze the medicine composition:")
            st.markdown("### Step 1: Upload an Image")
            st.write("Use the uploader above to upload an image of the medicine label.")
            st.markdown("### Step 2: Analyze the Image")
            st.write("Click the 'Analyze Uploaded Image' button (displayed after uploading image) to get detailed insights about the medicine.")

with tab2:
    st.header("Example Images")
    example_images = {
        "Example 1": "images/benadryl.jpeg",
        "Example 2": "images/dolo.jpeg",
    }

    cols = st.columns(2)
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

st.warning("💡 **Disclaimer:** This information is intended for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional for diagnosis and treatment.")
# Footer
st.markdown("---")
st.write("Made with ❤️ by [Shravan] (https://github.com/tallashravan/)")