library(scholar)

id <- 'Maj9ubYAAAAJ&hl'
publications <- get_publications(id, flush = TRUE) %>% tibble()

write.csv(df, "scholar.csv", row.names = FALSE)

