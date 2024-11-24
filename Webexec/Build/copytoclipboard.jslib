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
    }
});
