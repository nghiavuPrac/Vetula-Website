// Speech-to-text functionality
$(document).ready(function() {
    if ('webkitSpeechRecognition' in window) {
        var recognition = new webkitSpeechRecognition();
        var speechIcon = document.getElementById('speechIcon');
        var recordingIndicator = document.getElementById('recordingIndicator');
        var searchInput = document.getElementById('form51');
        var startSound = document.getElementById('startSound');
        var stopSound = document.getElementById('stopSound');
        var isRecording = false
        // var recognitionTimeout; // Variable to hold the recognition timeout

        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function() {
            // clearTimeout(recognitionTimeout); // Clear any existing timeouts
            isRecording = true
            speechIcon.classList.add('recording');
            recordingIndicator.style.opacity = 1;
            searchInput.placeholder = 'Listening...';
            startSound.play(); // Play the start sound
        }

        recognition.onend = function() {
            isRecording = false
            speechIcon.classList.remove('recording');
            recordingIndicator.style.opacity = 0;
            searchInput.placeholder = 'Search';
            stopSound.play(); // Play the stop sound
        }

        speechIcon.addEventListener('click', function() {
            searchInput.focus(); // Focus on the search input field
            recognition.addEventListener("result",e=>{
                const transcript = Array.from(e.results)
                .map(result => result[0])
                .map(result => result.transcript)
                searchInput.value = transcript;   
            });

            if (isRecording){
                recognition.stop()
            }
            else{
                recognition.start();
            }
            
        });
    }
});