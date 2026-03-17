import { useState, useRef, useCallback, useEffect } from "react";

interface CrisisAnalysis {
  status: string;
  analysis: string;
  model: string;
}

export function ImageCrisisAnalyzer() {
  const [image, setImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CrisisAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startCamera = useCallback(async () => {
    try {
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" }
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
      setVideoReady(false);
      setError(null);
    } catch (err) {
      console.error("Camera error:", err);
      setError("Could not access camera. Please grant camera permissions.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
    setVideoReady(false);
  }, []);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
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

  const retakePhoto = useCallback(() => {
    setImage(null);
    setImageFile(null);
    setResult(null);
    setError(null);
    startCamera();
  }, [startCamera]);

  const handleAnalyze = useCallback(async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("crisis_type", "general");
      const res = await fetch("http://127.0.0.1:8000/api/crisis/analyze-image", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to analyze image");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [imageFile]);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-3 text-red-600">🚨 Crisis Scanner</h2>
      <p className="text-sm text-gray-600 mb-4">
        Take a photo of an accident or crisis. AI will analyze what's happening and tell you how to safely navigate away from danger.
      </p>

      {/* Camera View */}
      {cameraActive && (
        <div className="relative mb-4">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onLoadedMetadata={() => setVideoReady(true)}
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
            <p className="text-center text-yellow-600 text-sm mt-2">Starting camera...</p>
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

      {/* Buttons */}
      <div className="space-y-3">
        {!cameraActive && !image && (
          <button
            onClick={startCamera}
            className="w-full py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700"
          >
            📷 Take Photo
          </button>
        )}

        {image && !loading && !result && (
          <>
            <button
              onClick={handleAnalyze}
              className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700"
            >
              🔍 Analyze Crisis
            </button>
            <button
              onClick={retakePhoto}
              className="w-full py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300"
            >
              Retake Photo
            </button>
          </>
        )}
      </div>

      {loading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-red-600 border-t-transparent"></div>
          <p className="mt-2 text-gray-600">Analyzing with AI...</p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-300 rounded-lg">
          <h3 className="font-bold text-green-800 mb-2">Analysis Result</h3>
          <div className="whitespace-pre-wrap text-sm text-gray-800">{result.analysis}</div>
          <p className="mt-3 text-xs text-gray-500">Powered by: {result.model}</p>
        </div>
      )}
    </div>
  );
}
