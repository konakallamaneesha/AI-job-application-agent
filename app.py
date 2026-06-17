import streamlit as st
import os
import re
import backend.auto_apply as auto_apply_mod
from backend.auto_apply import (
    auto_apply,
    submit_application
)
from backend.location_extractor import (
    extract_location
)
from backend.pdf_reader import extract_text_from_pdf
from backend.skill_extractor import extract_skills

from backend.job_roles import (
    get_search_roles
)

from backend.job_search.internshala import (
    search_internshala,
    get_job_description
)

from backend.simple_matcher import (
    calculate_match
)

st.set_page_config(
    page_title="AI Job Application Agent",
    page_icon="🚀"
)

st.title("AI Job Application Agent")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

if uploaded_file:

    # Save Resume

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    resume_path = (
        f"uploads/{uploaded_file.name}"
    )

    with open(
        resume_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    st.success(
        "Resume uploaded successfully!"
    )

    text = extract_text_from_pdf(
        uploaded_file
    )

    st.subheader(
        "Extracted Resume Text"
    )

    st.text_area(
        "Resume Content",
        text,
        height=250
    )
    detected_location = extract_location(
        text
    )

    st.subheader(
        "Location Preferences"
    )

    locations = [

        "Work From Home",

        "Hyderabad",

        "Bangalore",

        "Chennai",

        "Pune",

        "Mumbai",

        "Delhi",

        "Any"

    ]

    if (
        detected_location
        and
        detected_location not in locations
    ):

        locations.insert(
            0,
            detected_location
        )

    default_index = 0

    if detected_location in locations:
        default_index = locations.index(
            detected_location
        )

    preferred_location = st.selectbox(
        "Select Preferred Location",
        locations,
        index=default_index
    )
    if st.button(
        "Extract Skills"
    ):

        # Extract Skills

        with st.spinner(
            "Analyzing Resume..."
        ):

            skills = extract_skills(
                text
            )

        st.subheader(
            "Extracted Skills"
        )

        st.write(
            skills
        )

        # Generate Search Roles

        roles = get_search_roles(
            skills
        )

        st.subheader(
            "Generated Search Roles"
        )

        st.write(
            roles
        )

        # Search Jobs

        st.subheader(
            "Searching Internships..."
        )

        jobs = []

        with st.spinner(
            "Searching Internshala..."
        ):

            for role in roles:

                try:

                    role_jobs = (
                        search_internshala(
                            role
                        )
                    )

                    jobs.extend(
                        role_jobs
                    )

                except Exception as e:

                    st.error(
                        f"Error searching {role}: {e}"
                    )

        # Match Jobs

        results = []

        with st.spinner(
            "Matching Resume With JD..."
        ):

            for job in jobs:

                try:

                    jd_skills = (
                        get_job_description(
                            job["url"]
                        )
                    )

                    if len(jd_skills) < 2:
                        continue

                    result = (
                        calculate_match(
                            skills,
                            jd_skills
                        )
                    )

                    results.append({

                        "title":
                        job["title"],

                        "company":
                        job.get(
                            "company",
                            "Not Available"
                        ),

                        "location":
                        job.get(
                            "location",
                            "Not Available"
                        ),

                        "score":
                        result["score"],

                        "matched":
                        result["matched"],

                        "missing":
                        result["missing"],

                        "required":
                        jd_skills,

                        "url":
                        job["url"],

                        "role":
                        job.get(
                            "query",
                            ""
                        )

                    })

                except Exception as e:

                    st.error(
                        f"Error matching internship: {e}"
                    )

        # Remove Duplicates

         # Remove Duplicates

        unique_results = []
        seen = set()

        for job in results:

            key = (
                job["title"],
                job["company"]
            )

            if key not in seen:

                seen.add(
                    key
                )

                unique_results.append(
                    job
                )

        results = unique_results

        # Location Filter

        if preferred_location != "Any":

            filtered_results = []

            for job in results:

                location = job[
                    "location"
                ].lower()

                if (
                    preferred_location.lower()
                    ==
                    "work from home"
                ):

                    if (
                        "work from home"
                        in location
                    ):

                        filtered_results.append(
                            job
                        )

                else:

                    if (

                        preferred_location.lower()
                        in location

                        or

                        "work from home"
                        in location

                    ):

                        filtered_results.append(
                            job
                        )

            results = filtered_results

        # Minimum Score Filter

        results = [

            job

            for job in results

            if job["score"] >= 50

        ]

        # Sort

        results.sort(

            key=lambda x: x["score"],

            reverse=True

        )
        st.session_state["results"] = results

        st.success(

            f"Found {len(results)} matching internships"

        )

        st.subheader(

            "🏆 Recommended Internships"

        )
    if "results" in st.session_state:

        results = st.session_state["results"]
        for job in results[:5]:

            st.markdown("---")

            st.write(
                f"### {job['title']}"
            )

            st.write(
                f"🏢 Company: {job['company']}"
            )

            st.write(
                f"📍 Location: {job['location']}"
            )

            st.write(
                f"🔍 Found Via: {job['role']}"
            )

            st.write(
                f"🎯 Match Score: {job['score']}%"
            )

            st.write(
                "✅ Matched Skills"
            )

            st.write(
                ", ".join(job["matched"])
            )

            st.write(
                "⚠️ Missing Skills"
            )

            st.write(
                ", ".join(job["missing"])
            )

            st.markdown(
                f"[🔗 Open Job]({job['url']})"
            )

            if st.button(
                f"🚀 Auto Apply - {job['title']}",
                key=job["url"]
            ):

                response = auto_apply(
                    job["url"],
                    resume_path
                )

                st.session_state["job_url"] = job["url"]
                st.session_state["resume_path"] = resume_path
                st.session_state["questions"] = response.get("questions", [])

                if response["status"] == "login_required":

                    st.warning(
                        "Please login in the opened browser and click Auto Apply again."
                    )

                elif response["status"] == "questions_found":

                    st.warning(
                        "Additional Questions Found"
                    )

                    question_prefix = f"answers_{job['url']}"

                    for q in response["questions"]:

                        key = (
                            f"{question_prefix}_"
                            f"{re.sub(r'[^a-zA-Z0-9]+', '_', q['label']).strip('_').lower()}"
                        )

                        if q["type"] == "textarea":

                            st.text_area(
                                q["label"],
                                key=key,
                                value=st.session_state.get(key, "")
                            )

                        elif q["type"] == "number":

                            st.number_input(
                                q["label"],
                                key=key,
                                value=st.session_state.get(key, 0),
                                step=1
                            )

                        elif q["type"] == "select":

                            options = q.get("options", [])

                            st.selectbox(
                                q["label"],
                                options,
                                key=key,
                                index=0 if options else None
                            )

                        elif q["type"] == "radio":

                            options = q.get("options", [])

                            st.radio(
                                q["label"],
                                options,
                                key=key,
                                index=0 if options else None
                            )

                        elif q["type"] == "checkbox":

                            st.checkbox(
                                q["label"],
                                key=key,
                                value=st.session_state.get(key, False)
                            )

                        else:

                            st.text_input(
                                q["label"],
                                key=key,
                                value=st.session_state.get(key, "")
                            )

                    if st.button(
                        "Submit Answers",
                        key=f"submit_answers_{job['url']}"
                    ):

                        answers = {}

                        for q in response["questions"]:

                            key = (
                                f"{question_prefix}_"
                                f"{re.sub(r'[^a-zA-Z0-9]+', '_', q['label']).strip('_').lower()}"
                            )

                            answers[q["label"]] = st.session_state.get(key, "")

                        response["status"] = "answers_ready"
                        st.session_state[f"{question_prefix}_answers"] = answers
                        st.session_state[f"{question_prefix}_ready"] = True

                        st.success("Answers Saved Successfully")
                        st.info("Answers are ready for the next step. Final submission will be implemented in Step 3.")

                elif response["status"] == "ready_for_confirmation":

                    st.session_state[
                        "ready_job"
                    ] = job["url"]

                    st.success(
                        "Resume Uploaded Successfully"
                    )

            if (
                "ready_job" in st.session_state
                and
                st.session_state["ready_job"]
                == job["url"]
            ):

                st.warning(
                    "Ready For Submission"
                )

                if st.button(
                    f"✅ Confirm Submit - {job['title']}",
                    key=f"confirm_{job['url']}"
                ):

                    question_prefix = f"answers_{st.session_state['job_url']}"
                    answers = {}

                    for question in st.session_state.get("questions", []):

                        key = (
                            f"{question_prefix}_"
                            f"{re.sub(r'[^a-zA-Z0-9]+', '_', question['label']).strip('_').lower()}"
                        )

                        if key in st.session_state:

                            answers[question["label"]] = st.session_state[key]

                    submit_result = submit_application(
                        st.session_state["job_url"],
                        st.session_state["resume_path"],
                        st.session_state.get("questions", []),
                        answers
                    )

                    if submit_result.get("status") == "submitted":

                        st.success(
                            "Application Submitted Successfully"
                        )

                    else:

                        st.error(
                            "Submission failed. Please try again."
                        )

            with st.expander(
                "View Required Skills"
            ):

                st.write(
                    job["required"]
                )