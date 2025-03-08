library(shiny)
library(scholar)
library(tidyverse)
library(DT)
library(bslib)
library(googlesheets4)
library(purrr)
library(htmltools)
library(swipeR)

# httr::GET("https://scholar.google.com")

options(gargle_oauth_cache = "secrets",
        gargle_oauth_email = "man.cebral@gmail.com")

gs4_auth()

#google scholar online 
#id <- 'YOUR GOOGLE SCHOLAR ID'
# publications <- get_publications(id, flush = TRUE) %>% tibble()
# l <- get_profile(id, flush=TRUE)
# myFields <- gsub("^.{0,2}", "", HTML(paste0(paste0("| ", l$fields))))

projects <- read_sheet("YOUR SHEET ID",
                       sheet = "projects") %>% 
  mutate(caption=paste(Name, Role, Year, Funder))

#offline
#saveRDS(publications, "data/publications.rds")
publications <- readRDS("data/publications.rds")
l <- readRDS("data/l.rds")
myFields <- gsub("^.{0,2}", "", HTML(paste0(paste0("| ", l$fields))))

#lista de videos
video_ids <- readRDS("data/myVideosIDs.rds")
video_ids <- video_ids[video_ids!=c("d13ez2yehOc", "SV47VHC6N6s")]

#imágenes de fondo
imagenesFondo <- c("https://raw.githubusercontent.com/mancebral/whiteCamera/refs/heads/main/wp-content/uploads/2015/06/zZZ.gif",
                   "https://raw.githubusercontent.com/mancebral/whiteCamera/refs/heads/main/wp-content/uploads/2015/06/Dh5P.gif",
                   "https://raw.githubusercontent.com/mancebral/whiteCamera/refs/heads/main/wp-content/uploads/2015/06/9hw9.gif",
                   "https://raw.githubusercontent.com/mancebral/whiteCamera/refs/heads/main/wp-content/uploads/2015/06/G1JQ.gif"
                   )

ui <- #page_fluid(
  fluidPage(
    
    tags$head(
      tags$link(rel = "stylesheet", 
                type = "text/css", 
                href = "myStyles.css")
    ),
    
    tags$head(
      tags$link(rel = "stylesheet", 
                href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css")
    ),
    
    tags$head(
      # Metadatos Open Graph (Facebook, WhatsApp, LinkedIn)
      tags$meta(property = "og:title", content = paste0(l$name, ", Ph.D")),
      tags$meta(property = "og:description", content = "personal website"),
      tags$meta(property = "og:image", content = sample(imagenesFondo, 1)),  # URL de la imagen
      tags$meta(property = "og:url", content = "https://manuel-cebral.shinyapps.io/personalWeb/"),
      tags$meta(property = "og:type", content = "website"),
      
      # Twitter Cards (para Twitter)
      tags$meta(name = "twitter:card", content = "summary_large_image"),
      tags$meta(name = "twitter:title", content = paste0(l$name, ", Ph.D")),
      tags$meta(name = "twitter:description", content = "personal website"),
      tags$meta(name = "twitter:image", content =  sample(imagenesFondo, 1))
    ),
    
    tags$head(
      tags$style(HTML("
            * {
        box-sizing: border-box;
      }
      
      .header {
        text-align: center;
        padding: 32px;
      }
      
      .row {
        display: -ms-flexbox; /* IE10 */
        display: flex;
        -ms-flex-wrap: wrap; /* IE10 */
        flex-wrap: wrap;
        padding: 0 4px;
      }
      
      /* Create four equal columns that sits next to each other */
      .column {
        -ms-flex: 25%; /* IE10 */
        flex: 25%;
        max-width: 25%;
        padding: 0 4px;
      }
      
      .column img {
        margin-top: 8px;
        vertical-align: middle;
        width: 100%;
      }
      
      /* Responsive layout - makes a two column-layout instead of four columns */
      @media screen and (max-width: 800px) {
        .column {
          -ms-flex: 50%;
          flex: 50%;
          max-width: 50%;
        }
      }
      
      /* Responsive layout - makes the two columns stack on top of each other instead of next to each other */
      @media screen and (max-width: 600px) {
        .column {
          -ms-flex: 100%;
          flex: 100%;
          max-width: 100%;
        }
      }

    "))
    ),
    
#### Application title #### 
    column(12, id="titleColumn",
           style = paste0("background-image: url(", sample(imagenesFondo,1),"); "),
           style="
           background-size: cover;
           background-position: center center;
           justify-content: center;
          align-items: center;
         color: white;",
           column(12, id="titleColumnElements",
                  titlePanel(paste0(l$name, ", Ph.D")),
                  #HTML(l$affiliation, "<br>", myFields
                  HTML(myFields
                  ),
                  HTML("<br><br>"),
                  HTML("<div id=menu><a href='#projectsColumn'>Projects</a><br>
         <a href='#publicationsColumn'>Publications</a><br>
         <a href='#videosColumn'>Videos</a><br>
         <a href='#aboutColumn'>About</a><br>
         <a href='#contactColumn'>Contact</a></div>")
           )
    ),
    
#### projects #### 
    fluidRow(
      column(12, id="projectsColumn",
             column(12,
                    HTML("<div id='header_2'>Projects</div")),
             column(12,
                    uiOutput("myProjects"),
                    HTML("<br>")
             )
      )),
    
#### publications #### 
    fluidRow(
      column(12, id="publicationsColumn",
             style = "background-color: #FFFFFF; padding: 20px; border-radius: 10px;",
             card(
               card_header("Publications",class = "header_3"),
               height = "100vh",
               style = "resize:vertical;",
               card_body(class = "body_3",
                         min_height = "100vh",
                         dataTableOutput("publications", width = "100%")
               ))
      )
    ),
    
    #### videos ####
fluidRow(
  column(12, id = "videosColumn",
         swipeR(
           id = "video_carousel",
           height = "315px", 
           width = "100%",
           keyboard = TRUE,
           loop = TRUE, 
           navigation = TRUE,
           pagination = FALSE,
           autoplay = FALSE,
           speed = 300,
           direction = "horizontal",
           slidesPerView = 1,
           thumbsPerView = 1,
           effect = "fade",
           wrapper = do.call(swipeRwrapper, lapply(video_ids, function(id) {
             tags$iframe(
               width = "100%", height = "315",
               src = paste0("https://www.youtube.com/embed/", id),
               frameborder = "0", allowfullscreen = NA
             )
           }))
         )
  )
),
    
    ####  about #### 
    fluidRow(
      column(12, id="aboutColumn",
             style = "background-color: #f1bf05; padding: 20px; border-radius: 10px;",
             HTML("<H3 id='aboutTitle'>About</H3>"),
             column(6, id="aboutColumnElements",
                    HTML('<h4>Short Bio</h4>
             <p style="margin-left: 0px; margin-right: 20px;">Manuel Cebral-Loureda is a philosopher specialized in Digital Humanities, 
             in which he applies computational tools -such as text mining, 
             sentiment analysis, natural language processing, machine learning or deep learning- 
             to humanistic objects of study. He also works in experimental research projects 
             based on human-centered technologies, cognitive and affective neurosciences and their 
             application in the education for human flourishing. He is currently an Assistant-Research Professor at 
             the Department of Humanistic Studies in the School of Humanities and Education in Campus Monterrey, 
             Tecnologico de Monterrey; as well as a Level II National Researcher (SNII) of CONAHCYT (Mexico).
                  </p>')
             ),
             
             column(6, id="aboutColumnElements",
                    HTML("<h4>Current  Positions</h4>
                     <div id='positions'>
                    <b>[2024 to present]</b> Member of the Mexican National System of Researchers (SNII) - Level II.<br> 
                    <b>[2023 to present]</b> Assistant Research Professor at Tecnologico de Monterrey.<br>
                    <b>[2023 to present]</b> Principal Investigator in Cartografías lingüísticas del miedo: un acercamiento inmersivo desde las Neurohumanidades approved by Ciencia de Frontera of Conahcyt Mexico.<br>
                    <b>[2023 to present]</b> Member of the research project desafIA, directed by Héctor Ceballos, together with CSIC Spain and Tecnológico de Monterrey.<br>
                    <b>[2023 to present]</b> Coordinator of the Research Group of Digital Methods and Cultural Analytics of the Research Dean's Office of the Faculty of Humanities and Education.<br>
                    <b>[2022 to present]</b> Principal Investigator in Neurohumanities Lab. Engaging Experiences for Human Flourishing approved in the Challenge Based Research Funding Program of Tecnológico de Monterrey.<br>
                    <b>[2021 to present]</b> Researcher at Projects of Human Flourishing, directed by Enrique Tamés, at Tecnológico de Monterrey.<br>
                    <b>[2021 to present]</b> Member of the Building Reliable Advances and Innovations in Neurotechnology (BRAIN), international research network in neuroengineering.<br>
                    <b>[2021 to 2024]</b> Member of the Mexican National System of Researchers (SNI) - Level Candidate. <br>
                    <b>[2020 to present]</b> Coordinator of the Line of Generation and Application of Knowledge Digital Humanities and Posthumanism in the Doctoral Program of Humanistic Studies at Tecnológico de Monterrey.<br>
                    <b>[2020 to 2023]</b> Coordinator of the Seminar on Digital Humanities at Tecnológico de Monterrey.<br>
                    <b>[2019 to present]</b> Full-time professor at the School of Humanities and Education of Tecnológico de Monterrey, Department of Humanistic Studies.<br>
                  </div>")
             )
      )
    ),
    
    #### contact ####
    fluidRow(
      column(12, id="contactColumn",
             column(12, id="contactColumnElements",
                    HTML('<b>Manuel Cebral-Loureda, Ph.D</b><br>
                manuel.cebral[at]tec.mx<br>
                          <p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><span property="dct:title">Personal Website</span> licensed under <a href="https://creativecommons.org/licenses/by-nc/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""></a></p>
                          '),
                    div(class = "social-icons",
                        tags$a(href = "https://orcid.org/0000-0001-6359-2427", target = "_blank",
                               tags$i(class = "fa-brands fa-orcid")),
                        tags$a(href = "https://www.linkedin.com/in/manuel-cebral/", target = "_blank",
                               tags$i(class = "fa-brands fa-linkedin")),
                        tags$a(href = "https://www.youtube.com/@mancebral", target = "_blank",
                               tags$i(class = "fa-brands fa-brands fa-youtube")),
                        tags$a(href = "https://github.com/mancebral", target = "_blank",
                               tags$i(class = "fa-brands fa-brands fa-github"))
                    )
             )
      )
    )
  )

# Define server logic required to draw a histogram
server <- function(input, output) {
  
  nImages <- nrow(projects)
  
  #Calculate the number of images per column (4 in total)
  imageGrid <- paste(
    # Dividir las imágenes en grupos de 4 para crear una nueva fila por cada grupo
    purrr::map(1:ceiling(nImages / 4), function(row) {
      startIndex <- (row - 1) * 4 + 1
      endIndex <- min(row * 4, nImages)
      
      # Generar el HTML para cada fila
      paste0(
        "<div class='row'>", 
        paste(purrr::map(startIndex:endIndex, function(i) {
          paste0(
            "<div class='column'>", 
            "<a href='", projects[i, "link"], "' target='_blank'>",
            "<img src='", projects[i, "path"], "' style='width:100%'></a>",
            "<p class='text2'>", projects[i, "Name"], "</p>",
            "<p class='text3'>", 
            projects[i, "Role"], " | " ,
            projects[i, "Year"], " | " ,
            projects[i, "Funder"],
            "</p>",
            "</div>"
          )
        }), collapse = ""),
        "</div>"  # Cerrar la fila aquí
      )
    }), collapse = "")  # Concatenar todas las filas generadas
  
  #Paste the image grid HTML into Shiny
  output$myProjects = renderUI({
    HTML(imageGrid)
  })
  
  output$publications <- renderDT({
    publications %>% 
      mutate(title=paste0("<h4>", title, "</h4>", author, ". ", journal)) %>% 
      select(title, year, cites) %>% 
      datatable(rownames = FALSE, escape = FALSE,
                options = list(searching = FALSE, pageLength = 25,lengthChange = FALSE,
                               lengthMenu = c(50, 100, 500, 1000), scrollX = T#,
                               #width="100%",autoWidth = TRUE
                ))
  })
}

# Run the application 
shinyApp(ui = ui, server = server)

