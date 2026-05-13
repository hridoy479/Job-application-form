from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from supabase import create_client
import uuid

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SUPABASE CONFIG
SUPABASE_URL = "https://wfykauwgpgisnqfzgxip.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmeWthdXdncGdpc25xZnpneGlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY2NTc5OSwiZXhwIjoyMDk0MjQxNzk5fQ.Sv0ErCnBH7heF3A08HHKtw9rJhvzcfCSujhAfn0sdxc"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

@app.post("/upload-cv")
async def upload_cv(

    first_name: str = Form(...),
    last_name: str = Form(...),

    email: str = Form(...),

    phone: str = Form(...),

    availability: str = Form(...),

    experience: str = Form(...),

    cv: UploadFile = File(...)

):

    try:

        # FILE TYPE VALIDATION
        allowed_types = [

            "application/pdf",

            "application/msword",

            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        ]

        if cv.content_type not in allowed_types:

            return {
                "success": False,
                "error": "Only PDF, DOC, DOCX files allowed"
            }

        # UNIQUE FILE NAME
        extension = cv.filename.split(".")[-1]

        file_name = f"{uuid.uuid4()}.{extension}"

        # READ FILE
        file_bytes = await cv.read()

        # UPLOAD TO SUPABASE STORAGE
        upload_response = supabase.storage \
            .from_("cvs") \
            .upload(

                file_name,

                file_bytes,

                {
                    "content-type": cv.content_type
                }

            )

        # GET PUBLIC URL
        file_url = supabase.storage \
            .from_("cvs") \
            .get_public_url(file_name)

        # SAVE TO DATABASE
        insert_response = supabase.table("applications").insert({

            "first_name": first_name,

            "last_name": last_name,

            "email": email,

            "phone": phone,

            "availability": availability,

            "experience": experience,

            "cv_url": file_url

        }).execute()

        return {

            "success": True,

            "message": "Application submitted successfully",

            "cv_url": file_url

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }




@app.get("/applications", response_class=HTMLResponse)
def get_applications():

    response = supabase.table(
        "applications"
    ).select("*").execute()

    applications = response.data

    html = """

    <html>

    <head>

        <title>Applications</title>

        <style>

            body{
                font-family: Arial;
                padding:40px;
                background:#f4f4f4;
            }

            table{
                width:100%;
                border-collapse: collapse;
                background:white;
            }

            th, td{
                border:1px solid #ddd;
                padding:12px;
                text-align:left;
            }

            th{
                background:black;
                color:white;
            }

            a{
                color:blue;
            }

        </style>

    </head>

    <body>

        <h1>Submitted Applications</h1>

        <table>

            <tr>

                <th>Name</th>

                <th>Email</th>

                <th>Phone</th>

                <th>Availability</th>

                <th>Experience</th>

                <th>CV</th>

                <th>Date</th>

            </tr>

    """

    for app in applications:

        html += f"""

        <tr>

            <td>
                {app['first_name']} {app['last_name']}
            </td>

            <td>
                {app['email']}
            </td>

            <td>
                {app['phone']}
            </td>

            <td>
                {app['availability']}
            </td>

            <td>
                {app['experience']}
            </td>

            <td>
                <a href="{app['cv_url']}" target="_blank">
                    View CV
                </a>
            </td>

            <td>
                {app['created_at']}
            </td>

        </tr>

        """

    html += """

        </table>

    </body>

    </html>

    """

    return html


@app.get("/form", response_class=HTMLResponse)
def form_page():

    return """

    <html>

    <head>

        <title>Career Form</title>

        <style>

            body{
                font-family:Arial;
                background:#f4f4f4;
                padding:40px;
            }

            .form-wrapper{
                max-width:700px;
                margin:auto;
                background:white;
                padding:30px;
                border-radius:10px;
            }

            input,
            textarea{
                width:100%;
                padding:12px;
                margin-top:10px;
                margin-bottom:20px;
                border:1px solid #ccc;
                border-radius:5px;
            }

            button{
                background:black;
                color:white;
                padding:14px 20px;
                border:none;
                cursor:pointer;
            }

            .radio-group{
                margin-bottom:20px;
            }

            .radio-group label{
                margin-right:20px;
            }

            #message{
                margin-top:20px;
                font-weight:bold;
            }

        </style>

    </head>

    <body>

        <div class="form-wrapper">

            <h1>Job Application Form</h1>

            <form
                id="career-form"
                enctype="multipart/form-data"
            >

                <input
                    type="text"
                    name="first_name"
                    placeholder="First Name"
                    required
                >

                <input
                    type="text"
                    name="last_name"
                    placeholder="Last Name"
                    required
                >

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    required
                >

                <input
                    type="text"
                    name="phone"
                    placeholder="Phone Number"
                    required
                >

                <div class="radio-group">

                    <label>
                        <input
                            type="radio"
                            name="availability"
                            value="Part Time"
                            required
                        >
                        Part Time
                    </label>

                    <label>
                        <input
                            type="radio"
                            name="availability"
                            value="Casual"
                        >
                        Casual
                    </label>

                    <label>
                        <input
                            type="radio"
                            name="availability"
                            value="Full Time"
                        >
                        Full Time
                    </label>

                </div>

                <input
                    type="file"
                    name="cv"
                    accept=".pdf,.doc,.docx"
                    required
                >

                <textarea
                    name="experience"
                    rows="5"
                    placeholder="Write your experience..."
                    required
                ></textarea>

                <button type="submit">
                    Submit Application
                </button>

                <p id="message"></p>

            </form>

        </div>

        <script>

        document
        .getElementById("career-form")
        .addEventListener("submit", async function(e){

            e.preventDefault();

            const form = this;

            const message =
                document.getElementById("message");

            message.innerText = "Uploading...";

            const formData = new FormData(form);

            try {

                const response = await fetch(
                    "/upload-cv",
                    {
                        method:"POST",
                        body:formData
                    }
                );

                const result =
                    await response.json();

                if(result.success){

                    message.innerText =
                        "Application submitted successfully.";

                    form.reset();

                }else{

                    message.innerText =
                        result.error;

                }

            } catch(error){

                message.innerText =
                    "Something went wrong.";

            }

        });

        </script>

    </body>

    </html>

    """