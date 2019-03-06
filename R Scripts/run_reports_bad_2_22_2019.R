#Non-Fatal Opioid Overdose Clusters in Baltimore, MD
#This script runs the Bad Batch Alert team .Rmd file, and then e-mails the resulting report.

# get the necessary packages
library(rmarkdown)
library(RDCOMClient)
library(tesseract)
library(pdftools)
library(extrafont)

# Last Updated 2/19/2019

setwd("O:/Production/Workspace")

# specify pandoc path
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")

# Bad Batch
rmarkdown::render(input="./bad_batch_2_22_2019.Rmd", output_format="pdf_document",
                  output_file = paste(gsub("-", "_", Sys.Date()),"Bad_Batch.pdf",  sep = "_"),
                  output_dir = paste("O:/Production/Workspace/Bad Batch/BadBatch", Sys.Date(),
                                     sep = "_"))

## e-mail the resulting report ##
OutApp <- COMCreate("Outlook.Application")

# Send Logic --------------------------------------------------------------

# Uses PDF to Text and searches for string to base e-mail send logic on. Added on 2/19/2019.
bad_report<-paste(paste("O:\\Production\\Workspace\\Bad Batch\\BadBatch", Sys.Date(), sep = "_"),
                  paste(gsub("-", "_", Sys.Date()),"Bad_Batch.pdf",  sep = "_"), sep = '/')

file_check<- pdftools::pdf_text(bad_report)

# Find "No Overdose Clusters in PDF of Report"
# returns position if string identified (don't send). Returns -1 if not identified (send!).
search_string<-regexpr('No Overdose Clusters Detected', file_check)

################ Bad Batch #################
sysdate2<-gsub("-","_",as.character(Sys.Date()))
myFile<-paste("O:\\Production\\Workspace\\Bad Batch\\BadBatch","_",Sys.Date(),"\\",sysdate2,"_Bad_Batch",".pdf",sep="")

if(file.exists(myFile) & search_string[[1]]==-1){
  ## create an email 
  outMail1 = OutApp$CreateItem(0)
  
  ## configure  email parameter. Multiple addresses, use semi-colons.
  outMail1[["To"]] = "ENTER EMAIL ADDRESSES HERE"
  outMail1[["subject"]] = "Non-fatal overdose spike alert"
  outMail1[["body"]] = 
"Bad Batch,Attached is a spike alert.
This is an automated report, and my e-mail is typically only checked during business hours."
  
  ## Add Attachment
  outMail1[["Attachments"]]$Add(myFile)
                                      
  
  ## send it                     
  outMail1$Send()
}else{
  outMail2 = OutApp$CreateItem(0)
  outMail2[["To"]] = "ENTER EMAIL ADDRESSES HERE"
  outMail2[["subject"]] = "No Clusters Detected"
  outMail2[["body"]] = 
"Bad Batch,
No Clusters were detected today.
Note: This is an automated report, and my e-mail is typically only checked during business hours."
  
  ## send it                     
  outMail2$Send()
  }