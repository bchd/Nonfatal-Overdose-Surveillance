#Non-Fatal Opioid Overdose Clusters in Baltimore, MD
#This script runs the epidemiology and outreach team .Rmd files, and then e-mails the resulting reports.


# Loads libraries. Use install.packages() first-----------------------------------------------------------------------
library(rmarkdown)
library(RDCOMClient)
library(tesseract)
library(pdftools)
library(extrafont)

# Sets Workplace Directories and Paths ------------------------------------

# Sets Workplace Directory
setwd("O:/Production/Workspace/Workspace_Test")

# specify pandoc path
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")


# Renders Reports using R Markdown ----------------------------------------
# render the outreach markdown report 
rmarkdown::render(input="./outreach_test_2_22_2019.Rmd", output_format="pdf_document",
                  output_file = paste(gsub("-", "_", Sys.Date()),"Outreach_Report.pdf",  sep = "_"),
                  output_dir = paste("O:/Production/Workspace/Workspace_Test/Outreach/Out", Sys.Date(),
                                     sep = "_"))


# render the epidemiology markdown report 
rmarkdown::render(input="./epi_test_2_22_2019.Rmd", output_format="pdf_document",
                  output_file = paste(gsub("-", "_", Sys.Date()),"Epidemiology_Report.pdf",  sep = "_"),
                  output_dir = paste("O:/Production/Workspace/Workspace_Test/Epidemiology/Epi", Sys.Date(),
                                     sep = "_"))

# Send Logic --------------------------------------------------------------

# Uses PDF to Text and searches for string to base e-mail send logic on. Added on 2/6/2019.

# Send Logic: If the Epi (or Outreach PDF ~) Pdf does NOT contain "NO SIGNIFICANT CLUSTERS HAVE BEEN IDENTIFIED'
epi_report<-paste(paste("O:\\Production\\Workspace\\Workspace_Test\\Epidemiology\\Epi", Sys.Date(), sep = "_"),
                  paste(gsub("-", "_", Sys.Date()),"Epidemiology_Report.pdf",  sep = "_"), sep = '/')

file_check<- pdftools::pdf_text(epi_report)

# Find "NO SIGNIFICANT CLUSTERS HAVE BEEN IDENTIFIED"
search_string<-regexpr('NO SIGNIFICANT CLUSTERS HAVE BEEN IDENTIFIED', file_check)

# Sends OUTREACH TEAM E-MAIL----------------------------------------------------------

## e-mail the resulting report ##
OutApp <- COMCreate("Outlook.Application")

## create an email 
outMail1 = OutApp$CreateItem(0)

## configure  email parameter. Multiple addresses, separate with a semi-colon.
outMail1[["To"]] = "ENTER EMAIL ADDRESSES HERE"

outMail1[["subject"]] = "Outreach Team Cluster Report"
if (search_string[[1]]==-1){
outMail1[["body"]] = 
"Colleagues,

A cluster(s) was detected.  See attached *.PDF.

When considering outreach, consider: 
1) The number of non-fatal overdoses in the cluster
2) Geographic size of the cluster
3) Number of days the cluster has been active.

Note: This is an automated report, and my e-mail is typically only checked during business hours."
}else{
outMail1[["body"]] = 
"Colleagues,
  
No cluster was detected. See attached *.PDF for citywide timeseries and neighborhood information.
  
When considering outreach, consider: 
1) The number of non-fatal overdoses in the cluster
2) Geographic size of the cluster
3) Number of days the cluster has been active. 
  
Note: This is an automated report, and my e-mail is typically only checked during business hours."
  
}
## Add Attachment
outMail1[["Attachments"]]$Add(paste(paste("O:\\Production\\Workspace\\Workspace_Test\\Outreach\\Out", Sys.Date(), sep = "_"),
                                    paste(gsub("-", "_", Sys.Date()),"Outreach_Report.pdf",  sep = "_"), sep = '/'))

## send it                     
outMail1$Send()


# Sends EPIDEMIOLOGY TEAM E-MAIL----------------------------------------------------------
## create an email 
#outMail2 = OutApp$CreateItem(0)

## configure  email parameter. Multiple addresses, string concatenate?
#outMail2[["To"]] = "ENTER EMAIL ADDRESSES HERE"
#outMail2[["subject"]] = "Epidemiology Team Cluster Report"

#if (search_string[[1]]==-1){
#outMail2[["body"]] =
#"Colleagues,

#A cluster(s) was detected. See attached *.PDF.

#When considering outreach, consider:
#1) The number of non-fatal overdoses in the cluster
#2) Geographic size of the cluster
#3) Number of days the cluster has been active. 

#Note: This is an automated report, and my e-mail is typically only checked during business hours."

#}else{
#outMail2[["body"]] =
#"Colleagues,

#No cluster was detected. See attached *.PDF for citywide timeseries and neighborhood information.

#When considering outreach, consider:
#1) The number of non-fatal overdoses in the cluster
#2) Geographic size of the cluster
#3) Number of days the cluster has been active. 

#Note: This is an automated report, and my e-mail is typically only checked during business hours."

#}
# Add Attachment
#outMail2[["Attachments"]]$Add(paste(paste("O:\\Production\\Workspace\\Workspace_Test\\Epidemiology\\Epi", Sys.Date(), sep = "_"),
                                    #paste(gsub("-", "_", Sys.Date()),"Epidemiology_Report.pdf",  sep = "_"), sep = '/'))

# send it
#outMail2$Send()


# Sends Separate Outreach TEAM E-MAIL only when there is a cluster.----------------------------------------------------------

if (search_string[[1]]==-1){
  ## create an email 
  outMail3 = OutApp$CreateItem(0)
  
  outMail3[["To"]] = "ENTER EMAIL ADDRESSES HERE"
  
  outMail3[["subject"]] = "Separate Outreach Team Cluster Report"
  outMail3[["body"]] = "Colleagues,
  
  A cluster(s) was detected. See attached *.PDF.

  When considering outreach, consider: 
  1) The number of non-fatal overdoses in the cluster
  2) Geographic size of the cluster
  3) Number of days the cluster has been active."
  
  ## Add Attachment
  outMail3[["Attachments"]]$Add(paste(paste("O:\\Production\\Workspace\\Workspace_Test\\Outreach\\Out", Sys.Date(), sep = "_"),
                                      paste(gsub("-", "_", Sys.Date()),"Outreach_Report.pdf",  sep = "_"), sep = '/'))
  
  ## send it                     
  outMail3$Send()
  
}else{
}

### END OF PROGRAM
