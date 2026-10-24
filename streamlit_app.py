import streamlit as st
from spanish import run_spanish_learning_pipeline, check_exercises

st.set_page_config(page_title="Spanish Learning Pipeline", layout="wide")

st.title("🇪🇸 Spanish Learning Pipeline")
st.write("Analyze your Spanish writing, create exercises, and get AI feedback!")

# Initialize session state for storing results
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None

# Input section
st.subheader("Enter Your Spanish Text")
spanish_input = st.text_area(
    "Paste your Spanish text here:",
    placeholder="Example: Yo como una manzana en el parque cada día...",
    height=120,
    key="spanish_input"
)

# Run pipeline button
if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
    if not spanish_input.strip():
        st.error("Please enter some Spanish text first!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.info("📝 Processing your request...")
            progress_bar.progress(25)

            with st.spinner("Running pipeline..."):
                result = run_spanish_learning_pipeline(spanish_input)
                st.session_state.pipeline_result = result
                st.session_state.feedback = None

            progress_bar.progress(100)
            status_text.success("✅ Pipeline Complete!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.progress(0)

# Results section with tabs
st.divider()
st.subheader("Results")

if st.session_state.pipeline_result is None:
    st.warning("📝 Please enter Spanish text above and click 'Run Pipeline' to see results here.")
else:
    result = st.session_state.pipeline_result

    # Create tabs for each stage
    stage1_tab, stage2_tab, stage3_tab, stage4_tab = st.tabs(["Stage 1: Analysis", "Stage 2: Reading", "Stage 3: Exercises", "Stage 4: Feedback"])

    with stage1_tab:
        st.write(result["stages"].get("analysis", "No analysis available"))

    with stage2_tab:
        reading_ex = result["stages"].get("reading_exercise", {})
        if reading_ex.get("text"):
            st.write("**Refined Text:**")
            st.write(reading_ex.get("text"))
        if reading_ex.get("words"):
            st.write("**Word Metadata:**")
            st.dataframe(reading_ex.get("words"))
        if not reading_ex:
            st.info("No reading exercise data available")

    with stage3_tab:
        exercises_text = result["stages"].get("exercises", "No exercises available")

        # Remove the "Answers:" section from display
        if "Answers:" in exercises_text:
            questions_only = exercises_text.split("Answers:")[0].strip()
        else:
            questions_only = exercises_text

        # Parse questions with blanks
        lines = questions_only.split('\n')
        numbered_items = []
        for line in lines:
            if line.strip() and len(line.strip()) > 0 and line.strip()[0].isdigit() and '.' in line:
                numbered_items.append(line)

        st.subheader("Fill in the blanks:")

        # Create HTML display for better formatting
        user_answers_dict = {}

        html_content = '<div style="font-family: Arial, sans-serif; line-height: 2; font-size: 16px;">'

        for idx, item in enumerate(numbered_items, 1):
            parts = item.split('_______')

            if len(parts) > 1:
                html_content += f'<div style="margin: 20px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">'
                html_content += f'<span>{parts[0]}</span>'
                html_content += f'<input type="text" id="blank_{idx}" style="border: none; border-bottom: 2px solid #555; padding: 5px 8px; width: 140px; font-size: 16px;" placeholder="">'
                html_content += f'<span>{parts[1] if len(parts) > 1 else ""}</span>'
                html_content += f'</div>'
            else:
                html_content += f'<div style="margin: 20px 0; padding: 10px;">{item}</div>'

        html_content += '</div>'

        st.markdown(html_content, unsafe_allow_html=True)

        # Input fields below for collecting answers
        st.write("")
        for idx in range(1, len(numbered_items) + 1):
            user_answers_dict[idx] = st.text_input(
                label=f"Answer {idx}:",
                label_visibility="collapsed",
                key=f"answer_input_{idx}",
                placeholder=f"Type answer {idx}"
            )

        st.divider()

        if st.button("✓ Check My Answers", type="primary", use_container_width=True):
            if not all(user_answers_dict.values()):
                st.error("Please fill in all blanks before checking!")
            else:
                formatted_answers = "\n".join([f"{i}. {user_answers_dict[i]}" for i in range(1, len(user_answers_dict) + 1)])

                with st.spinner("Checking your answers..."):
                    feedback = check_exercises(exercises_text, formatted_answers)
                    st.session_state.feedback = feedback
                st.success("✅ Answers checked!")

    with stage4_tab:
        if st.session_state.feedback is None:
            st.info("💡 Fill in your answers in Stage 3 and click 'Check My Answers' to see feedback here.")
        else:
            st.write(st.session_state.feedback)

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("""
    This pipeline helps you learn Spanish by:
    1. **Analyzing** your writing for grammar & style
    2. **Creating** interactive reading exercises
    3. **Generating** 5 types of practice exercises
    4. **Checking** your answers with detailed feedback
    """)

    st.divider()
    st.write("📚 Model: Claude Haiku")
