mergeInto(LibraryManager.library, {
   
    CopyToClipboard: function(text) {
        // Convert Unity's string to a JS string
        const str = UTF8ToString(text);
        // Use Clipboard API to copy text
        navigator.clipboard.writeText(str).then(() => {
            console.log(`Copied to clipboard: ${str}`);
        }).catch(err => {
            console.error('Failed to copy text to clipboard', err);
        });
    },
    
    OpenFileDialog: function(objectName, methodName) {
        
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.style.display = 'none';

        fileInput.onchange = function(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                console.log(`Target Object: ${objectName}`);
                 console.log(`Target method: ${methodName}`);
                //SendMessage(objectName, methodName, e.target.result);
                SendMessage('InteractionUI', 'OnFileSelected', e.target.result);
            };
            
            reader.readAsText(file);
        };

        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    },
    GetQueryString: function() {
        if (typeof window !== 'undefined' && window.location) {
            return allocateUTF8(window.location.search);
        }
        return allocateUTF8('');
    },
    DownloadFile: function(filename, content) {
        // Convert filename and content from UTF8 strings
        const fileName = UTF8ToString(filename);
        const fileContent = UTF8ToString(content);

        // Create a Blob with the content
        const blob = new Blob([fileContent], { type: 'text/plain' });

        // Create a link element
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = fileName; // Set the download filename
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});
