/**
 * NFC Handler using Web NFC API
 * Compatible with Chrome on Android
 */

class NFCHandler {
    constructor() {
        this.isSupported = 'NDEFReader' in window;
        this.reader = null;
        this.isScanning = false;
    }

    /**
     * Check if NFC is supported
     */
    checkSupport() {
        if (!this.isSupported) {
            throw new Error('Web NFC is not supported on this device. Please use Chrome on Android.');
        }
        return true;
    }

    /**
     * Read NFC tag
     */
    async readTag(onSuccess, onError) {
        try {
            this.checkSupport();

            if (this.isScanning) {
                throw new Error('Already scanning for NFC tags');
            }

            this.reader = new NDEFReader();
            this.isScanning = true;

            await this.reader.scan();
            console.log('NFC scan started');

            this.reader.addEventListener('reading', ({ message, serialNumber }) => {
                console.log('NFC tag detected:', serialNumber);

                // Format serial number
                const tagId = serialNumber;

                // Read tag data if available
                let tagData = null;
                if (message.records.length > 0) {
                    const textDecoder = new TextDecoder();
                    for (const record of message.records) {
                        if (record.recordType === 'text') {
                            tagData = textDecoder.decode(record.data);
                            break;
                        }
                    }
                }

                if (onSuccess) {
                    onSuccess({
                        tagId: tagId,
                        data: tagData,
                        message: message
                    });
                }
            });

            this.reader.addEventListener('readingerror', () => {
                console.error('NFC read error');
                if (onError) {
                    onError(new Error('Failed to read NFC tag'));
                }
            });

        } catch (error) {
            this.isScanning = false;
            console.error('NFC Error:', error);
            if (onError) {
                onError(error);
            }
        }
    }

    /**
     * Write data to NFC tag
     */
    async writeTag(data, onSuccess, onError) {
        try {
            this.checkSupport();

            const writer = new NDEFReader();

            // Prepare NDEF message
            const records = [{
                recordType: 'text',
                data: data
            }];

            await writer.write({ records });

            console.log('NFC tag written successfully');
            if (onSuccess) {
                onSuccess();
            }

        } catch (error) {
            console.error('NFC Write Error:', error);
            if (onError) {
                onError(error);
            }
        }
    }

    /**
     * Stop scanning
     */
    stopScan() {
        if (this.reader && this.isScanning) {
            // Note: Web NFC API doesn't have explicit stop method
            // Scanning stops when page is unloaded or reader is garbage collected
            this.isScanning = false;
            this.reader = null;
            console.log('NFC scan stopped');
        }
    }

    /**
     * Request NFC permission (implicit in scan())
     */
    async requestPermission() {
        try {
            this.checkSupport();
            // Permission is requested automatically when scan() is called
            return true;
        } catch (error) {
            console.error('NFC Permission Error:', error);
            return false;
        }
    }
}

// Export for use in other scripts
window.NFCHandler = NFCHandler;
