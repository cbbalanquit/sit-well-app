import streamlit as st
import requests
import json
import time
from PIL import Image
import io

# Configure page
st.set_page_config(
    page_title="Posture Monitor",
    page_icon="🧍",
    layout="wide"
)

API_URL = "http://localhost:8080"  # Your API backend URL

st.title("Posture Monitor")
st.markdown("Monitor your sitting posture to prevent back pain and improve ergonomics.")

st.sidebar.header("Controls")
analysis_mode = st.sidebar.radio("Select Mode:", ["Single Image", "Real-time Analysis"])

if analysis_mode == "Single Image":
    st.header("Posture Analysis")

    source = st.radio("Choose input source:", ["Upload Image", "Take Photo"])

    if source == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Uploaded Image", use_column_width=True)

            # Analyze button
            analyze_btn = st.button("Analyze Posture")

            if analyze_btn:
                with st.spinner('Analyzing posture...'):
                    buf = io.BytesIO()
                    image.save(buf, format='JPEG')
                    image_bytes = buf.getvalue()

                    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
                    try:
                        response = requests.post(f"{API_URL}/posture/analyze", files=files)

                        if response.status_code == 200:
                            result = response.json()

                            # Display results
                            with col2:
                                if result['status'] == 'success':
                                    st.success(f"Posture Quality: {result.get('posture_quality', 'Unknown').upper()}")

                                    if result.get('issues'):
                                        st.subheader("Issues Detected:")
                                        for issue in result['issues']:
                                            st.warning(f"• {issue}")

                                    if result.get('recommendations'):
                                        st.subheader("Recommendations:")
                                        for rec in result['recommendations']:
                                            st.info(f"• {rec}")
                                else:
                                    st.error("No person detected in the image.")
                        else:
                            st.error(f"Error from API: {response.status_code}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend service: {str(e)}")
                        st.info("Make sure your backend is running at " + API_URL)

    elif source == "Take Photo":
        img_file_buffer = st.camera_input("Take a picture")

        if img_file_buffer is not None:
            # Get bytes data
            image_bytes = img_file_buffer.getvalue()

            # Display and analyze options
            col1, col2 = st.columns(2)

            # Analyze button
            analyze_btn = st.button("Analyze Posture")

            if analyze_btn:
                with st.spinner('Analyzing posture...'):
                    # Send to backend
                    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
                    try:
                        response = requests.post(f"{API_URL}/posture/analyze", files=files)

                        if response.status_code == 200:
                            result = response.json()

                            # Display results
                            with col2:
                                if result['status'] == 'success':
                                    st.success(f"Posture Quality: {result.get('posture_quality', 'Unknown').upper()}")
                                    
                                    if 'annotated_image' in result:
                                        st.image(result['annotated_image'], caption="Posture Analysis", use_column_width=True)

                                    if result.get('issues'):
                                        st.subheader("Issues Detected:")
                                        for issue in result['issues']:
                                            st.warning(f"• {issue}")

                                    if result.get('recommendations'):
                                        st.subheader("Recommendations:")
                                        for rec in result['recommendations']:
                                            st.info(f"• {rec}")
                                else:
                                    st.error("No person detected in the image.")
                        else:
                            st.error(f"Error from API: {response.status_code}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend service: {str(e)}")
                        st.info("Make sure your backend is running at " + API_URL)

else:
    st.header("Real-time Posture Monitoring")
    st.warning("Note: For the POC demo, real-time analysis will require WebSocket implementation. This feature is under development.")
    st.info("For a real implementation, you would need to:")
    st.markdown("""
    1. Establish WebSocket connection with the backend
    2. Capture frames from the camera at regular intervals
    3. Send frames to the backend for analysis
    4. Display real-time feedback
    """)

    # Placeholder for future implementation
    st.write("This section will be implemented in the next iteration.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Your Team | POC Demo")
