
Colors = []
base_style = """
<style>

    #MainMenu { 
        visibility: hidden;
        
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
        margin: 0;
        padding: 0;
    }

    .custom-navbar {
        position: fixed;
        height: 0%;
        display: flex;
        width : 100%;
        background-color: #e0fbfc;
        margin-top:0;
        padding-top:0;
        color: black;
       
        margin-bottom: 0px;
        z-index: 10000;
    }

    .custom-navbar h2 {
        margin: 0;
        padding: 0;
        font-size: 3rem;
    }

    /* Remove padding from the main content container */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Optional: remove margin on main if needed */
    .main {
        margin-top: 0rem !important;
    }

</style>


"""