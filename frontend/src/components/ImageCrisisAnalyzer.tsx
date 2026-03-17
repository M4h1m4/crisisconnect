import { useState, useRef, useCallback } from "react";

interface Props {
  onAnalyze: (imageFile: File) => void;
  loading?: boolean;
}

export function ImageCrisisAnalyzer({ onAnalyze, loading }: Props) {
  const [image, setImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startCamera = useCallback(async () => {
    console.log("[Camera] Starting camera...");
    setError(null);
    setVideoReady(false);
    
    const tryCamera = async (facingMode: string) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        return stream;
      } catch {
        return null;
      }
    };

    let stream = await tryCamera("environment");
    console.log("[Camera] Tried environment:", !!stream);
    if (!stream) stream = await tryCamera("user");
    console.log("[Camera] Tried user:", !!stream);
    if (!stream) stream = await tryCamera("true");
    console.log("[Camera] Tried true:", !!stream);

    if (!stream) {
      console.log("[Camera] No camera found");
      setError("No camera found. Please use 'Upload Photo' instead.");
      return;
    }

    streamRef.current = stream;
    console.log("[Camera] Stream obtained, attaching to video element");
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      console.log("[Camera] Attached to video element");
    }
    setCameraActive(true);
    console.log("[Camera] Camera active set to true");
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
    setVideoReady(false);
  }, []);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      setError("Camera not ready. Please wait a moment and try again.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
      setImage(dataUrl);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "crisis-image.jpg", { type: "image/jpeg" });
          setImageFile(file);
        }
      }, "image/jpeg");

      stopCamera();
    }
  }, [stopCamera]);

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setImage(ev.target?.result as string);
        setImageFile(file);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const retakePhoto = useCallback(() => {
    setImage(null);
    setImageFile(null);
    setError(null);
    startCamera();
  }, [startCamera]);

  const handleAnalyze = useCallback(() => {
    if (!imageFile) return;
    onAnalyze(imageFile);
  }, [imageFile, onAnalyze]);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-3 text-red-600">🚨 Crisis Scanner</h2>
      <p className="text-sm text-gray-600 mb-4">
        Take a photo or upload an image of an accident. AI will analyze what's happening and guide you to safety with your location.
      </p>

      {/* Camera View */}
      {cameraActive && (
        <div className="mb-4">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onLoadedMetadata={() => {
              console.log("Metadata loaded, video ready");
              setVideoReady(true);
            }}
            onCanPlay={() => {
              console.log("Can play");
              setVideoReady(true);
            }}
            className="w-full rounded-lg bg-black"
          />
          <div className="mt-2 flex gap-2">
            <button
              onClick={captureImage}
              disabled={!videoReady}
              className="flex-1 py-2 bg-white border-2 border-gray-300 text-black font-bold rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              📷 Capture
            </button>
            <button
              onClick={stopCamera}
              className="py-2 px-4 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
          {!videoReady && (
            <p className="text-center text-yellow-600 text-sm mt-2">Waiting for camera...</p>
          )}
        </div>
      )}

      {/* Captured Image */}
      {image && !cameraActive && (
        <div className="mb-4">
          <img src={image} alt="Captured" className="w-full rounded-lg border" />
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Buttons */}
      <div className="space-y-3">
        {!cameraActive && !image && (
          <>
            <button
              onClick={startCamera}
              className="w-full py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700"
            >
              📷 Take Photo
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700"
            >
              📁 Upload Photo
            </button>
          </>
        )}

        {image && !loading && (
          <>
            <button
              onClick={handleAnalyze}
              className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700"
            >
              🔍 Analyze & Get Help
            </button>
            <button
              onClick={retakePhoto}
              className="w-full py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300"
            >
              Retake / Choose Different
            </button>
          </>
        )}
      </div>

      {loading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-red-600 border-t-transparent"></div>
          <p className="mt-2 text-gray-600">Analyzing image with your location...</p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
