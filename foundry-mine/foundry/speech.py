"""
 Utility class encapsulating the Azure Foundry Tools Speech SDK (Previously Cognitive Services Speech SDK) 
 Pre-requisites: 
    - Azure Speech Resource
    - azure-cognitiveservices-speech==1.48.2

 References:
    - Getting Started: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text
    - Speech SDK Documentation: https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech?view=azure-python
    - VS Code Azure AI Speech Toolkit: https://marketplace.visualstudio.com/items?itemName=ms-azureaispeech.azure-ai-speech-toolkit
    - Voice Names: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices
"""

import traceback

from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speechsdk

from .setup import FoundrySetup

class FoundrySpeechService:
    """Utility class to provide speech capabilities to Azure Foundry Agents"""
    
    def __init__(self, setup: FoundrySetup, voice_name: str = "en-US-JennyMultilingualNeural"):
        """
        Initialize the Speech Object with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
            voice_name: The name of the voice to use for speech synthesis
        """
        try:
            self.setup = setup
            self.voice_name = voice_name

            self.speech_endpoint = self.setup.env_settings["SPEECH_ENDPOINT"]
            self.speech_region = self.setup.env_settings["SPEECH_REGION"]
            self.speech_resource_id = self.setup.env_settings["SPEECH_RESOURCE_ID"]

            print("Endpoint:", self.speech_endpoint)
            print("Region:", self.speech_region)
            print("Resource ID:", self.speech_resource_id)

            # Build the SpeechConfig using the aad# token format required by the Speech SDK
            self.speech_config = speechsdk.SpeechConfig(
                auth_token=f"aad#{self.speech_resource_id}#{self.setup.token}",
                region=self.speech_region,
            )
            self.speech_config.speech_synthesis_voice_name = self.voice_name

        except Exception as e:
            print(f"\n❌ Error during __init__: {e}")
            traceback.print_exc()
    #end of function: __init__

    def text_to_speech(self, text: str, output_filename: str):
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: The input text to convert to speech
            output_filename: The filename (including path) where the output audio will be saved
        """
        try:
            print(f"Converting text to speech. Output file: {output_filename}")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"✅ Speech synthesis completed successfully. Audio saved to: {output_filename}")
            else:
                print(f"❌ Speech synthesis failed. Reason: {result.reason}")
                if result.error_details:
                    print(f"Error details: {result.error_details}")
            return result

        except Exception as e:
            print(f"\n❌ Error during text_to_speech: {e}")
            traceback.print_exc()
            return None
    #end of function: text_to_speech


    def speech_to_text(self, input_audio_filename: str, output_filename: str,language: str = "en-US") -> str:
        """
        Convert speech to text from an audio file.
        
        Args:
            input_audio_filename: The filename (including path) of the input audio file
            language: The language of the speech in the audio file (default is "en-US")
        Returns:
            The recognized text from the audio, or None if recognition failed
            Also writes the recognized text to the specified output filename
        """
        try:
            print(f"Converting speech to text. Input file: {input_audio_filename}")
            audio_config = speechsdk.audio.AudioConfig(filename=input_audio_filename)
            recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

            result = recognizer.recognize_once_async().get()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"✅ Speech recognition completed successfully. Recognized text: {result.text}")
                # Optionally save the transcription to a file
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(result.text)
                    print(f"Saved to {output_filename}")
                return result.text
            else:
                print(f"❌ Speech recognition failed. Reason: {result.reason}")
                if result.error_details:
                    print(f"Error details: {result.error_details}")
                return None 

        except Exception as e:
            print(f"\n❌ Error during speech_to_text: {e}")
            traceback.print_exc()
            return None
    #end of function: speech_to_text