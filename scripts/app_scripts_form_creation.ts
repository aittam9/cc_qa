function createFormFromSheet() {
  // Get the active spreadsheet and the first sheet
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  
  // Get all data from the sheet
  const data = sheet.getDataRange().getValues();
  // Remove header row
  const questions = data.slice(1);
  let sheet_name = ss.getName()
  // Create a new form
  const form = FormApp.create('Valutazione domande su Codice Civile (${ss.getName()})');
  form.setDescription('Indicazioni: \nDi seguito ti verranno mostrati degli articoli del codice civile italiano accoppiati con una domanda. Insieme, testo dell\'articolo e domanda, formano un quesito che ammette una risposta binaria, di tipo "SI"o "NO"\n\nIl tuo compito è stabilire se la domanda è adatta al contenuto del testo e se possa trovare risposta in esso.\nLa risposta alla domanda deve essere strettamente contenuta nel testo, ovvero il testo deve contenere informazioni sufficienti per poter formulare una risposta esaustiva e pertinente alla domanda.\n\nEsempio:\nArt. 1 La capacità giuridica si acquisisce al momento della nascita.\nDomanda valida:\nQuando si acquisisce la capacità giuridica?\n\nDomanda NON valida:\nCosa comporta la capacità giuridica?\n\nNOTA BENE:\nIl tuo compito non è rispondere alla domanda sulla base del testo, ma stabilire se la risposta alla domanda possa essere trovata nel passaggio di testo.');
  
  // Enable collecting email addresses to track responses
  form.setCollectEmail(true);
  
  // Create a linked spreadsheet to store responses
  const destSpreadsheet = SpreadsheetApp.create('Form_Responses_' + form.getTitle()+ ss.getName());
  form.setDestination(FormApp.DestinationType.SPREADSHEET, destSpreadsheet.getId());
  
  // Set initial page explaining the process
  form.addSectionHeaderItem()
    .setTitle('Welcome')
    .setHelpText(
      'Il presente form è diviso in 10 pagine contenenti 10 quesiti ognuna, per un totale di 100 quesiti.\n' +
      'Puoi completare il form in più sessioni, registrandoti con una mail.\n' +
      'I tuoi progressi verranno salvati automaticamente al termine di ogni pagina, una volta premuto il pulsante "Next".\n' +
      'Puoi tornare al form in un secondo momento e riprendere da dove hai lasciato collegandoti nuovamente al link e inserendo il tuo indirizzo e-mail.'
    );
    
  // Add email validation message
  form.setCustomClosedFormMessage(
    'This form requires a valid email address to track your progress. ' +
    'Please make sure you use the same email address when returning to complete additional sections.'
  );

  // Calculate number of pages needed
  const questionsPerPage = 10;
  const totalPages = Math.ceil(questions.length / questionsPerPage);
  
  // Create a grid item to track completion
  const progressItem = form.addGridItem();
  progressItem.setTitle('Per favore, spunta la dicitura qui sotto per iniziare a tenere traccia dei progressi.')
    .setRows(['Progress'])
    .setColumns(['Started'])
    .setValidation(FormApp.createGridValidation()
      .requireLimitOneResponsePerColumn()
      .build());
  progressItem.setHelpText('Progress tracking');
  
  // Create pages and add questions
  for (let pageNum = 0; pageNum < totalPages; pageNum++) {
    // Add page break for all pages except the first
    if (pageNum > 0) {
      const pageBreak = form.addPageBreakItem();
      pageBreak.setTitle(`Section ${pageNum + 1} of ${totalPages}`)
        .setHelpText(
          `Quesiti ${pageNum * questionsPerPage + 1} - ${Math.min((pageNum + 1) * questionsPerPage, questions.length)}\n` +
          'Le tue risposte verranno salvate quando premi"Next" o "Submit".\n' +
          'Puoi condurre la valutazione anche in momenti separati, scanditi dal cambio di pagina'+
          'Ricordati di premere "Next" per cambiare pagina e salvare le domande terminate in questa sezione'
        );
    }
    
    // Create a question group for this page
    const questionGroup = form.addSectionHeaderItem()
      .setTitle(`Questions ${pageNum * questionsPerPage + 1} - ${Math.min((pageNum + 1) * questionsPerPage, questions.length)}`);
    
    // Get questions for current page
    const pageQuestions = questions.slice(
      pageNum * questionsPerPage,
      Math.min((pageNum + 1) * questionsPerPage, questions.length)
    );
    
    // Add questions to the page
    pageQuestions.forEach(([id, title, questionText]) => {
      const questionItem = form.addMultipleChoiceItem();
      questionItem.setTitle(`${questionText}`)
        .setChoices([
          questionItem.createChoice('SI'),
          questionItem.createChoice('NO')
        ])
        .setRequired(false); // Make questions optional to allow partial completion
      
      // Store the question ID in the help text
      //questionItem.setHelpText(`Question ID: ${id}`);
    });
    
    // Add navigation help text at the bottom of each page
    const navHelp = form.addSectionHeaderItem()
      .setTitle('Navigation')
      .setHelpText(
        pageNum < totalPages - 1 
          ? 'Premi "Next" per salvare e continuare con la prossima pagina.\nSe lo desideri puoi fermarti e riprendere più da tardi da dove hai lasciato'
          : 'Click "Submit" to save your responses.\nYou can return later to modify your answers if needed.'
      );
  }
  
  // Set custom confirmation message
  form.setConfirmationMessage(
    'Your responses have been saved!\n\n' +
    'If you have more sections to complete, you can return to the form using the same email address.\n' +
    'Your progress will be restored when you return.\n\n' +
    'Thank you for your participation!'
  );
  
  // Form settings
  form.setAcceptingResponses(true)
    .setAllowResponseEdits(true)
    .setProgressBar(true)
    .setShowLinkToRespondAgain(true)
    .setShuffleQuestions(false);
  
  // Create progress tracking sheet
  const progressSheet = destSpreadsheet.insertSheet('Progress Tracking');
  progressSheet.getRange('A1:E1').setValues([['Timestamp', 'Email', 'Section Completed', 'Questions Answered', 'Total Progress']]);
  
  // Create URLs sheet
  const urlSheet = ss.insertSheet('Form URLs');
  urlSheet.getRange('A1:B1').setValues([['Published URL', 'Edit URL']]);
  urlSheet.getRange('A2:B2').setValues([[form.getPublishedUrl(), form.getEditUrl()]]);
  urlSheet.autoResizeColumns(1, 2);
  
  // Set up the trigger for the response spreadsheet
  const triggerId = ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(destSpreadsheet)
    .onFormSubmit()
    .create()
    .getUniqueId();
  
  // Log the URLs
  Logger.log('Form URL: ' + form.getPublishedUrl());
  Logger.log('Form edit URL: ' + form.getEditUrl());
  Logger.log('Response Spreadsheet URL: ' + destSpreadsheet.getUrl());
}

function onFormSubmit(e) {
  const sheet = e.source;
  const progressSheet = sheet.getSheetByName('Progress Tracking');
  
  const timestamp = new Date();
  const email = e.namedValues['Email Address'][0];
  
  // Count answered questions (excluding email and progress tracking)
  const answeredQuestions = Object.entries(e.namedValues)
    .filter(([key, value]) => 
      key !== 'Email Address' && 
      key !== 'Progress Tracking (Do not modify)' && 
      value[0] !== ''
    ).length;
  
  // Get the form to calculate total questions
  const form = FormApp.openById(sheet.getFormUrl().match(/[-\w]{25,}/)[0]);
  const totalQuestions = form.getItems().filter(item => 
    item.getType() === FormApp.ItemType.MULTIPLE_CHOICE
  ).length;
  
  // Calculate section completed and total progress
  const sectionCompleted = Math.ceil(answeredQuestions / 10);
  const totalProgress = Math.round((answeredQuestions / totalQuestions) * 100);
  
  // Add progress to tracking sheet
  progressSheet.appendRow([
    timestamp,
    email,
    sectionCompleted,
    answeredQuestions,
    totalProgress + '%'
  ]);
}
