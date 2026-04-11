import { useState, useEffect, useRef } from "react";

const ISSUES = [
  { id: "RPT-2841", type: "Pothole", location: "Banjara Hills Rd 12", lat: 17.415, lng: 78.448, risk: 87, status: "In Progress", reporter: "ravi_k", date: "2026-04-09", priority: "Critical", ward: "Ward 10" },
  { id: "RPT-2839", type: "Broken Streetlight", location: "Jubilee Hills Check Post", lat: 17.432, lng: 78.408, risk: 61, status: "Assigned", reporter: "priya_m", date: "2026-04-09", priority: "High", ward: "Ward 8" },
  { id: "RPT-2836", type: "Illegal Waste Dumping", location: "Madhapur Near HITEC City", lat: 17.447, lng: 78.376, risk: 74, status: "Pending", reporter: "salman_r", date: "2026-04-08", priority: "High", ward: "Ward 15" },
  { id: "RPT-2834", type: "Pothole", location: "Ameerpet Junction", lat: 17.437, lng: 78.434, risk: 92, status: "Pending", reporter: "divya_s", date: "2026-04-08", priority: "Critical", ward: "Ward 6" },
  { id: "RPT-2831", type: "Damaged Footpath", location: "Somajiguda Circle", lat: 17.424, lng: 78.455, risk: 45, status: "Resolved", reporter: "arjun_p", date: "2026-04-07", priority: "Medium", ward: "Ward 9" },
  { id: "RPT-2829", type: "Open Manhole", location: "Kukatpally Housing Board", lat: 17.492, lng: 78.397, risk: 95, status: "Assigned", reporter: "meera_v", date: "2026-04-07", priority: "Critical", ward: "Ward 18" },
  { id: "RPT-2826", type: "Broken Streetlight", location: "Gachibowli Stadium Rd", lat: 17.440, lng: 78.352, risk: 55, status: "Resolved", reporter: "ravi_k", date: "2026-04-06", priority: "Medium", ward: "Ward 20" },
  { id: "RPT-2821", type: "Illegal Waste Dumping", location: "Tolichowki Junction", lat: 17.400, lng: 78.416, risk: 68, status: "Pending", reporter: "suresh_n", date: "2026-04-06", priority: "High", ward: "Ward 7" },
];

const TYPE_COLORS = {
  "Pothole": "#FF4444",
  "Broken Streetlight": "#FFB800",
  "Illegal Waste Dumping": "#FF6B35",
  "Damaged Footpath": "#8B5CF6",
  "Open Manhole": "#EF4444",
};

const STATUS_COLORS = {
  "Pending": { bg: "#FEF3C7", text: "#92400E", dot: "#F59E0B" },
  "Assigned": { bg: "#DBEAFE", text: "#1E40AF", dot: "#3B82F6" },
  "In Progress": { bg: "#EDE9FE", text: "#5B21B6", dot: "#8B5CF6" },
  "Resolved": { bg: "#D1FAE5", text: "#065F46", dot: "#10B981" },
};

const PRIORITY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3 };

// ─── Mini GIS Heatmap ──────────────────────────────────────────────────────
function HeatmapCanvas({ reports }) {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Draw stylized Hyderabad map grid
    ctx.fillStyle = "#0D1117";
    ctx.fillRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = "#1E2D3D";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 20) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += 20) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // Major roads (stylized)
    ctx.strokeStyle = "#1A3A5C";
    ctx.lineWidth = 3;
    const roads = [
      [[0.1, 0.5], [0.9, 0.5]], [[0.5, 0.1], [0.5, 0.9]],
      [[0.1, 0.3], [0.9, 0.7]], [[0.2, 0.8], [0.8, 0.2]],
      [[0.0, 0.6], [0.4, 0.4], [0.8, 0.6]],
    ];
    roads.forEach(pts => {
      ctx.beginPath();
      pts.forEach(([fx, fy], i) => i === 0 ? ctx.moveTo(fx * W, fy * H) : ctx.lineTo(fx * W, fy * H));
      ctx.stroke();
    });

    // Lat/Lng bounds for Hyderabad region
    const latMin = 17.37, latMax = 17.52;
    const lngMin = 78.33, lngMax = 78.50;

    const toXY = (lat, lng) => ({
      x: ((lng - lngMin) / (lngMax - lngMin)) * W,
      y: H - ((lat - latMin) / (latMax - latMin)) * H,
    });

    // Draw heat blobs
    reports.forEach(r => {
      const { x, y } = toXY(r.lat, r.lng);
      const radius = 20 + (r.risk / 100) * 35;
      const intensity = r.risk / 100;
      const color = r.risk > 80 ? [255, 50, 50] : r.risk > 60 ? [255, 150, 0] : [100, 200, 255];
      const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
      grad.addColorStop(0, `rgba(${color[0]},${color[1]},${color[2]},${intensity * 0.85})`);
      grad.addColorStop(0.5, `rgba(${color[0]},${color[1]},${color[2]},${intensity * 0.3})`);
      grad.addColorStop(1, "rgba(0,0,0,0)");
      ctx.beginPath();
      ctx.fillStyle = grad;
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Dot
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color[0]},${color[1]},${color[2]},1)`;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Ward labels
    ctx.fillStyle = "#2A4A6A";
    ctx.font = "9px monospace";
    ["HITEC", "Jubilee", "Ameerpet", "Gachibowli", "Kukatpally"].forEach((label, i) => {
      ctx.fillText(label, 20 + i * 68, 15 + (i % 2) * 10);
    });
  }, [reports]);
  return <canvas ref={canvasRef} width={420} height={260} style={{ width: "100%", height: "auto", borderRadius: "8px", display: "block" }} />;
}

// ─── Risk Badge ────────────────────────────────────────────────────────────
function RiskBadge({ score }) {
  const color = score >= 80 ? "#FF4444" : score >= 60 ? "#FF8800" : score >= 40 ? "#F59E0B" : "#10B981";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ position: "relative", width: 36, height: 36 }}>
        <svg width="36" height="36" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15" fill="none" stroke="#1E293B" strokeWidth="3" />
          <circle cx="18" cy="18" r="15" fill="none" stroke={color} strokeWidth="3"
            strokeDasharray={`${(score / 100) * 94} 94`} strokeLinecap="round" transform="rotate(-90 18 18)" />
        </svg>
        <span style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9, fontWeight: 700, color, fontFamily: "monospace" }}>{score}</span>
      </div>
    </div>
  );
}

// ─── Status Pill ───────────────────────────────────────────────────────────
function StatusPill({ status }) {
  const s = STATUS_COLORS[status] || STATUS_COLORS["Pending"];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 5, padding: "3px 10px", borderRadius: 20, background: s.bg, color: s.text, fontSize: 11, fontWeight: 600, fontFamily: "'Courier New', monospace" }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: s.dot, display: "inline-block" }} />
      {status}
    </span>
  );
}

// ─── AI Analysis Modal ─────────────────────────────────────────────────────
function AIAnalysisModal({ onClose, onSubmit }) {
  const [step, setStep] = useState(0);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [editedType, setEditedType] = useState("");
  const [editedRisk, setEditedRisk] = useState(0);
  const [description, setDescription] = useState("");

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target.result);
    reader.readAsDataURL(f);
    setStep(1);
  };

  const runAnalysis = () => {
    setAnalyzing(true);
    setStep(2);
    setTimeout(() => {
      const types = ["Pothole", "Broken Streetlight", "Illegal Waste Dumping", "Damaged Footpath", "Open Manhole"];
      const detected = types[Math.floor(Math.random() * types.length)];
      const risk = Math.floor(50 + Math.random() * 45);
      setResult({ type: detected, risk, lat: 17.415 + Math.random() * 0.08, lng: 78.35 + Math.random() * 0.12 });
      setEditedType(detected);
      setEditedRisk(risk);
      setAnalyzing(false);
      setStep(3);
    }, 2800);
  };

  const handleSubmit = () => {
    onSubmit({ type: editedType, risk: editedRisk, description, preview });
    onClose();
  };

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 16, width: "100%", maxWidth: 520, maxHeight: "90vh", overflowY: "auto" }}>
        {/* Header */}
        <div style={{ padding: "20px 24px 16px", borderBottom: "1px solid #1E293B", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 11, color: "#22D3EE", letterSpacing: 2, fontFamily: "monospace", marginBottom: 2 }}>AI ANALYSIS ENGINE</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "#F1F5F9", fontFamily: "'Playfair Display', Georgia, serif" }}>Report New Issue</div>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "#64748B", fontSize: 20, cursor: "pointer" }}>✕</button>
        </div>

        <div style={{ padding: 24 }}>
          {/* Steps */}
          <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
            {["Upload", "Geolocate", "AI Scan", "Review"].map((s, i) => (
              <div key={s} style={{ flex: 1, textAlign: "center" }}>
                <div style={{ width: 28, height: 28, borderRadius: "50%", margin: "0 auto 4px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, fontFamily: "monospace", background: step >= i ? "#22D3EE" : "#1E293B", color: step >= i ? "#0D1117" : "#475569", transition: "all 0.3s" }}>{i + 1}</div>
                <div style={{ fontSize: 9, color: step >= i ? "#22D3EE" : "#475569", fontFamily: "monospace", letterSpacing: 1 }}>{s.toUpperCase()}</div>
              </div>
            ))}
          </div>

          {/* Step 0: Upload */}
          {step === 0 && (
            <label style={{ display: "block", border: "2px dashed #1E293B", borderRadius: 12, padding: 40, textAlign: "center", cursor: "pointer", transition: "border-color 0.2s" }}
              onMouseOver={e => e.currentTarget.style.borderColor = "#22D3EE"}
              onMouseOut={e => e.currentTarget.style.borderColor = "#1E293B"}>
              <input type="file" accept="image/*" onChange={handleFile} style={{ display: "none" }} />
              <div style={{ fontSize: 32, marginBottom: 12 }}>📸</div>
              <div style={{ color: "#94A3B8", fontFamily: "monospace", fontSize: 13 }}>Tap to upload photo of issue</div>
              <div style={{ color: "#475569", fontSize: 11, marginTop: 6, fontFamily: "monospace" }}>GPS metadata will be auto-extracted</div>
            </label>
          )}

          {/* Step 1: Preview + Geolocate */}
          {step === 1 && (
            <div>
              {preview && <img src={preview} alt="preview" style={{ width: "100%", maxHeight: 200, objectFit: "cover", borderRadius: 8, marginBottom: 16 }} />}
              <div style={{ background: "#0F172A", borderRadius: 8, padding: 14, marginBottom: 16, border: "1px solid #1E293B" }}>
                <div style={{ fontSize: 10, color: "#22D3EE", fontFamily: "monospace", letterSpacing: 2, marginBottom: 8 }}>GPS METADATA</div>
                <div style={{ fontSize: 12, color: "#94A3B8", fontFamily: "monospace" }}>
                  <div>LAT: 17.4150° N &nbsp;|&nbsp; LNG: 78.4480° E</div>
                  <div style={{ marginTop: 4 }}>ACCURACY: ±3m &nbsp;|&nbsp; ALT: 544m</div>
                  <div style={{ marginTop: 4 }}>TIMESTAMP: {new Date().toISOString()}</div>
                </div>
              </div>
              <button onClick={runAnalysis} style={{ width: "100%", padding: "12px 0", background: "linear-gradient(135deg, #22D3EE, #0EA5E9)", border: "none", borderRadius: 8, color: "#0D1117", fontWeight: 700, fontFamily: "monospace", letterSpacing: 1, fontSize: 13, cursor: "pointer" }}>
                ⚡ RUN AI ANALYSIS
              </button>
            </div>
          )}

          {/* Step 2: Analyzing */}
          {step === 2 && (
            <div style={{ textAlign: "center", padding: "32px 0" }}>
              <div style={{ width: 60, height: 60, border: "3px solid #1E293B", borderTop: "3px solid #22D3EE", borderRadius: "50%", margin: "0 auto 20px", animation: "spin 1s linear infinite" }} />
              <div style={{ color: "#22D3EE", fontFamily: "monospace", letterSpacing: 2, fontSize: 13, marginBottom: 8 }}>ANALYZING IMAGE...</div>
              {["Extracting features...", "Classifying issue type...", "Calculating risk score...", "Cross-referencing ward data..."].map((msg, i) => (
                <div key={i} style={{ color: "#475569", fontFamily: "monospace", fontSize: 11, marginTop: 4, opacity: 0.8 }}>{msg}</div>
              ))}
            </div>
          )}

          {/* Step 3: Result */}
          {step === 3 && result && (
            <div>
              <div style={{ background: "linear-gradient(135deg, #0F172A, #1A2332)", border: "1px solid #22D3EE40", borderRadius: 12, padding: 16, marginBottom: 16 }}>
                <div style={{ fontSize: 10, color: "#22D3EE", fontFamily: "monospace", letterSpacing: 2, marginBottom: 12 }}>AI DETECTION RESULT</div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div>
                    <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>DETECTED TYPE</div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: TYPE_COLORS[result.type] || "#F1F5F9", fontFamily: "'Playfair Display', serif", marginTop: 2 }}>{result.type}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>RISK SCORE</div>
                    <div style={{ fontSize: 28, fontWeight: 900, color: result.risk >= 80 ? "#FF4444" : result.risk >= 60 ? "#FF8800" : "#F59E0B", fontFamily: "monospace" }}>{result.risk}</div>
                  </div>
                </div>
                <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace" }}>
                  Confidence: 94.2% &nbsp;|&nbsp; Model: InfraVision-v3 &nbsp;|&nbsp; Priority: {result.risk >= 80 ? "CRITICAL" : result.risk >= 60 ? "HIGH" : "MEDIUM"}
                </div>
              </div>

              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 1, display: "block", marginBottom: 6 }}>EDIT CATEGORY (if AI is wrong)</label>
                <select value={editedType} onChange={e => setEditedType(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", background: "#0F172A", border: "1px solid #1E293B", borderRadius: 8, color: "#F1F5F9", fontFamily: "monospace", fontSize: 13 }}>
                  {["Pothole", "Broken Streetlight", "Illegal Waste Dumping", "Damaged Footpath", "Open Manhole"].map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 1, display: "block", marginBottom: 6 }}>ADDITIONAL DESCRIPTION</label>
                <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Describe the issue in detail..."
                  style={{ width: "100%", padding: "10px 12px", background: "#0F172A", border: "1px solid #1E293B", borderRadius: 8, color: "#F1F5F9", fontFamily: "monospace", fontSize: 12, resize: "vertical", minHeight: 72, boxSizing: "border-box" }} />
              </div>

              <button onClick={handleSubmit} style={{ width: "100%", padding: "13px 0", background: "linear-gradient(135deg, #10B981, #059669)", border: "none", borderRadius: 8, color: "#fff", fontWeight: 700, fontFamily: "monospace", letterSpacing: 2, fontSize: 13, cursor: "pointer" }}>
                ✓ SUBMIT REPORT
              </button>
            </div>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ─── Auth Screen ───────────────────────────────────────────────────────────
function AuthScreen({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("citizen");

  return (
    <div style={{ minHeight: "100vh", background: "#060A10", display: "flex", alignItems: "center", justifyContent: "center", padding: 16, position: "relative", overflow: "hidden" }}>
      {/* Background */}
      <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(ellipse at 20% 50%, #0E3A5A22 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, #0A2A3A22 0%, transparent 60%)" }} />
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(#0D1117 1px, transparent 1px), linear-gradient(90deg, #0D1117 1px, transparent 1px)", backgroundSize: "40px 40px", opacity: 0.4 }} />

      <div style={{ position: "relative", width: "100%", maxWidth: 420 }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: "linear-gradient(135deg, #22D3EE, #0EA5E9)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🗺️</div>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontSize: 26, fontWeight: 900, color: "#F1F5F9", fontFamily: "'Playfair Display', Georgia, serif", letterSpacing: -0.5 }}>InfraTrack</div>
              <div style={{ fontSize: 10, color: "#22D3EE", fontFamily: "monospace", letterSpacing: 3 }}>CIVIC INTELLIGENCE PLATFORM</div>
            </div>
          </div>
          <div style={{ color: "#475569", fontSize: 13, fontFamily: "monospace" }}>Real-time infrastructure grievance redressal</div>
        </div>

        <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 16, padding: 28 }}>
          {/* Toggle */}
          <div style={{ display: "flex", background: "#060A10", borderRadius: 8, padding: 4, marginBottom: 24 }}>
            {["login", "register"].map(m => (
              <button key={m} onClick={() => setMode(m)} style={{ flex: 1, padding: "8px 0", borderRadius: 6, border: "none", background: mode === m ? "#22D3EE" : "none", color: mode === m ? "#0D1117" : "#64748B", fontFamily: "monospace", fontWeight: 700, fontSize: 12, letterSpacing: 1, cursor: "pointer", transition: "all 0.2s" }}>
                {m === "login" ? "SIGN IN" : "REGISTER"}
              </button>
            ))}
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 10, color: "#64748B", fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>USERNAME</label>
            <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter username"
              style={{ width: "100%", padding: "11px 14px", background: "#060A10", border: "1px solid #1E293B", borderRadius: 8, color: "#F1F5F9", fontFamily: "monospace", fontSize: 13, boxSizing: "border-box" }} />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 10, color: "#64748B", fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>PASSWORD</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••"
              style={{ width: "100%", padding: "11px 14px", background: "#060A10", border: "1px solid #1E293B", borderRadius: 8, color: "#F1F5F9", fontFamily: "monospace", fontSize: 13, boxSizing: "border-box" }} />
          </div>

          {mode === "register" && (
            <div style={{ marginBottom: 14 }}>
              <label style={{ display: "block", fontSize: 10, color: "#64748B", fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>ROLE</label>
              <select value={role} onChange={e => setRole(e.target.value)}
                style={{ width: "100%", padding: "11px 14px", background: "#060A10", border: "1px solid #1E293B", borderRadius: 8, color: "#F1F5F9", fontFamily: "monospace", fontSize: 13 }}>
                <option value="citizen">Citizen</option>
                <option value="admin">Municipal Officer</option>
              </select>
            </div>
          )}

          <button onClick={() => onAuth(username || "ravi_k", role)}
            style={{ width: "100%", padding: "13px 0", marginTop: 8, background: "linear-gradient(135deg, #22D3EE, #0EA5E9)", border: "none", borderRadius: 8, color: "#0D1117", fontWeight: 700, fontFamily: "monospace", letterSpacing: 2, fontSize: 13, cursor: "pointer" }}>
            {mode === "login" ? "SIGN IN →" : "CREATE ACCOUNT →"}
          </button>

          {/* Demo shortcuts */}
          <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid #1E2533" }}>
            <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", textAlign: "center", marginBottom: 10, letterSpacing: 1 }}>DEMO ACCESS</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => onAuth("ravi_k", "citizen")} style={{ flex: 1, padding: "8px 0", background: "#0F172A", border: "1px solid #1E293B", borderRadius: 6, color: "#94A3B8", fontFamily: "monospace", fontSize: 11, cursor: "pointer" }}>👤 Citizen</button>
              <button onClick={() => onAuth("admin_ghmc", "admin")} style={{ flex: 1, padding: "8px 0", background: "#0F172A", border: "1px solid #FF440040", borderRadius: 6, color: "#FF8888", fontFamily: "monospace", fontSize: 11, cursor: "pointer" }}>🛡 Admin</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Citizen Dashboard ─────────────────────────────────────────────────────
function CitizenDashboard({ user, reports, onNewReport, onLogout }) {
  const myReports = reports.filter(r => r.reporter === user);
  const [showModal, setShowModal] = useState(false);
  const [allReports, setAllReports] = useState(reports);

  const handleSubmit = (data) => {
    const newR = {
      id: `RPT-${2850 + Math.floor(Math.random() * 10)}`,
      type: data.type, location: "Hyderabad (GPS)", lat: 17.41 + Math.random() * 0.08,
      lng: 78.35 + Math.random() * 0.12, risk: data.risk, status: "Pending",
      reporter: user, date: new Date().toISOString().slice(0, 10), priority: data.risk >= 80 ? "Critical" : data.risk >= 60 ? "High" : "Medium", ward: "Ward 10"
    };
    setAllReports(p => [newR, ...p]);
  };

  const myR = allReports.filter(r => r.reporter === user);
  const resolved = myR.filter(r => r.status === "Resolved").length;
  const pending = myR.filter(r => r.status === "Pending").length;
  const critical = myR.filter(r => r.risk >= 80).length;

  return (
    <div style={{ minHeight: "100vh", background: "#060A10", color: "#F1F5F9" }}>
      {showModal && <AIAnalysisModal onClose={() => setShowModal(false)} onSubmit={handleSubmit} />}

      {/* Top Bar */}
      <div style={{ background: "#0D1117", borderBottom: "1px solid #1E293B", padding: "14px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 0, zIndex: 100 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: "linear-gradient(135deg, #22D3EE, #0EA5E9)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>🗺️</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>InfraTrack</div>
            <div style={{ fontSize: 9, color: "#22D3EE", fontFamily: "monospace", letterSpacing: 2 }}>CITIZEN PORTAL</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#F1F5F9", fontFamily: "monospace" }}>{user}</div>
            <div style={{ fontSize: 10, color: "#64748B", fontFamily: "monospace" }}>Hyderabad</div>
          </div>
          <button onClick={onLogout} style={{ padding: "6px 12px", background: "#1E293B", border: "none", borderRadius: 6, color: "#94A3B8", fontFamily: "monospace", fontSize: 11, cursor: "pointer" }}>↩ Exit</button>
        </div>
      </div>

      <div style={{ maxWidth: 720, margin: "0 auto", padding: "20px 16px" }}>
        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 24 }}>
          {[
            { label: "MY REPORTS", value: myR.length, color: "#22D3EE", icon: "📋" },
            { label: "RESOLVED", value: resolved, color: "#10B981", icon: "✅" },
            { label: "CRITICAL", value: critical, color: "#FF4444", icon: "⚠️" },
          ].map(s => (
            <div key={s.label} style={{ background: "#0D1117", border: `1px solid ${s.color}22`, borderRadius: 12, padding: "14px 16px" }}>
              <div style={{ fontSize: 18 }}>{s.icon}</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: s.color, fontFamily: "monospace", marginTop: 4 }}>{s.value}</div>
              <div style={{ fontSize: 9, color: "#64748B", fontFamily: "monospace", letterSpacing: 1, marginTop: 2 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* New Report Button */}
        <button onClick={() => setShowModal(true)}
          style={{ width: "100%", padding: "16px 0", marginBottom: 24, background: "linear-gradient(135deg, #22D3EE, #0EA5E9)", border: "none", borderRadius: 12, color: "#0D1117", fontWeight: 800, fontFamily: "monospace", letterSpacing: 2, fontSize: 14, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
          <span style={{ fontSize: 20 }}>📸</span> REPORT NEW ISSUE
        </button>

        {/* My Reports */}
        <div style={{ marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 11, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2 }}>MY REPORTS</div>
          <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>{myR.length} total</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {myR.map(r => (
            <div key={r.id} style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: "14px 16px", display: "flex", gap: 12, alignItems: "flex-start" }}>
              <div style={{ width: 4, alignSelf: "stretch", borderRadius: 4, background: TYPE_COLORS[r.type] || "#64748B", flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6, gap: 8 }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#F1F5F9", fontFamily: "'Playfair Display', serif" }}>{r.type}</div>
                    <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginTop: 2 }}>📍 {r.location}</div>
                  </div>
                  <RiskBadge score={r.risk} />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <StatusPill status={r.status} />
                  <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace" }}>{r.id} · {r.date}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Public Tracker */}
        <div style={{ marginTop: 28, marginBottom: 12 }}>
          <div style={{ fontSize: 11, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 12 }}>PUBLIC RESOLUTION TRACKER</div>
          <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              {["Pending", "Assigned", "In Progress", "Resolved"].map(s => {
                const count = allReports.filter(r => r.status === s).length;
                const c = STATUS_COLORS[s];
                return (
                  <div key={s} style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 20, fontWeight: 900, color: c.dot, fontFamily: "monospace" }}>{count}</div>
                    <div style={{ fontSize: 9, color: "#475569", fontFamily: "monospace", marginTop: 2 }}>{s.toUpperCase()}</div>
                  </div>
                );
              })}
            </div>
            <div style={{ height: 4, background: "#0F172A", borderRadius: 4, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${(allReports.filter(r => r.status === "Resolved").length / allReports.length) * 100}%`, background: "linear-gradient(90deg, #10B981, #059669)", borderRadius: 4 }} />
            </div>
            <div style={{ fontSize: 10, color: "#64748B", fontFamily: "monospace", marginTop: 8 }}>
              Resolution rate: {Math.round((allReports.filter(r => r.status === "Resolved").length / allReports.length) * 100)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Admin Dashboard ───────────────────────────────────────────────────────
function AdminDashboard({ user, reports, onLogout }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [sortBy, setSortBy] = useState("risk");
  const [filterStatus, setFilterStatus] = useState("All");
  const [selectedReport, setSelectedReport] = useState(null);

  const sorted = [...reports].sort((a, b) => {
    if (sortBy === "risk") return b.risk - a.risk;
    if (sortBy === "priority") return PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority];
    if (sortBy === "date") return new Date(b.date) - new Date(a.date);
    return 0;
  }).filter(r => filterStatus === "All" || r.status === filterStatus);

  const statusCounts = ["Pending", "Assigned", "In Progress", "Resolved"].map(s => ({
    s, count: reports.filter(r => r.status === s).length,
  }));

  const TABS = ["overview", "reports", "heatmap", "analytics"];

  return (
    <div style={{ minHeight: "100vh", background: "#060A10", color: "#F1F5F9" }}>
      {/* Top Bar */}
      <div style={{ background: "#0D1117", borderBottom: "1px solid #1E293B", padding: "14px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 0, zIndex: 100 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: "linear-gradient(135deg, #FF4444, #DC2626)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>🛡</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>InfraTrack</div>
            <div style={{ fontSize: 9, color: "#FF6666", fontFamily: "monospace", letterSpacing: 2 }}>COMMAND CENTRE</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10B981", boxShadow: "0 0 8px #10B981" }} />
          <span style={{ fontSize: 11, color: "#94A3B8", fontFamily: "monospace" }}>LIVE</span>
          <button onClick={onLogout} style={{ padding: "6px 12px", background: "#1E293B", border: "none", borderRadius: 6, color: "#94A3B8", fontFamily: "monospace", fontSize: 11, cursor: "pointer", marginLeft: 8 }}>↩ Exit</button>
        </div>
      </div>

      {/* Tab Nav */}
      <div style={{ background: "#0A0F1A", borderBottom: "1px solid #1E293B", display: "flex", overflowX: "auto" }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setActiveTab(t)}
            style={{ padding: "12px 20px", border: "none", borderBottom: activeTab === t ? "2px solid #FF4444" : "2px solid transparent", background: "none", color: activeTab === t ? "#FF6666" : "#64748B", fontFamily: "monospace", fontSize: 11, letterSpacing: 1, cursor: "pointer", whiteSpace: "nowrap", transition: "all 0.2s" }}>
            {t.toUpperCase()}
          </button>
        ))}
      </div>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "20px 16px" }}>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12, marginBottom: 20 }}>
              {[
                { label: "TOTAL REPORTS", value: reports.length, color: "#22D3EE", icon: "📋" },
                { label: "CRITICAL (Risk 80+)", value: reports.filter(r => r.risk >= 80).length, color: "#FF4444", icon: "🚨" },
                { label: "PENDING ACTION", value: reports.filter(r => r.status === "Pending").length, color: "#F59E0B", icon: "⏳" },
                { label: "RESOLVED TODAY", value: reports.filter(r => r.status === "Resolved").length, color: "#10B981", icon: "✅" },
              ].map(s => (
                <div key={s.label} style={{ background: "#0D1117", border: `1px solid ${s.color}22`, borderRadius: 12, padding: "16px 18px" }}>
                  <div style={{ fontSize: 20 }}>{s.icon}</div>
                  <div style={{ fontSize: 28, fontWeight: 900, color: s.color, fontFamily: "monospace", marginTop: 6 }}>{s.value}</div>
                  <div style={{ fontSize: 9, color: "#64748B", fontFamily: "monospace", letterSpacing: 1, marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Status breakdown */}
            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 18, marginBottom: 16 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 14 }}>STATUS PIPELINE</div>
              {statusCounts.map(({ s, count }) => {
                const c = STATUS_COLORS[s];
                return (
                  <div key={s} style={{ marginBottom: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                      <span style={{ fontSize: 11, fontFamily: "monospace", color: c.dot }}>{s}</span>
                      <span style={{ fontSize: 11, fontFamily: "monospace", color: "#64748B" }}>{count}</span>
                    </div>
                    <div style={{ height: 6, background: "#0F172A", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${(count / reports.length) * 100}%`, background: c.dot, borderRadius: 3, transition: "width 0.8s ease" }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Top priority issues */}
            <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 10 }}>⚡ AI PRIORITY ENGINE — TOP THREATS</div>
            {[...reports].sort((a, b) => b.risk - a.risk).slice(0, 3).map(r => (
              <div key={r.id} style={{ background: "#0D1117", border: "1px solid #FF444422", borderRadius: 10, padding: "12px 14px", marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#F1F5F9", fontFamily: "'Playfair Display', serif" }}>{r.type}</div>
                  <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginTop: 2 }}>📍 {r.location} · {r.ward}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                  <RiskBadge score={r.risk} />
                  <StatusPill status={r.status} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === "reports" && (
          <div>
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                style={{ padding: "8px 12px", background: "#0D1117", border: "1px solid #1E293B", borderRadius: 8, color: "#94A3B8", fontFamily: "monospace", fontSize: 11 }}>
                <option value="risk">Sort: Risk Score</option>
                <option value="priority">Sort: Priority</option>
                <option value="date">Sort: Date</option>
              </select>
              <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                style={{ padding: "8px 12px", background: "#0D1117", border: "1px solid #1E293B", borderRadius: 8, color: "#94A3B8", fontFamily: "monospace", fontSize: 11 }}>
                {["All", "Pending", "Assigned", "In Progress", "Resolved"].map(s => <option key={s}>{s}</option>)}
              </select>
              <div style={{ marginLeft: "auto", fontSize: 10, color: "#64748B", fontFamily: "monospace", alignSelf: "center" }}>{sorted.length} reports</div>
            </div>

            {sorted.map(r => (
              <div key={r.id} onClick={() => setSelectedReport(selectedReport?.id === r.id ? null : r)}
                style={{ background: "#0D1117", border: `1px solid ${selectedReport?.id === r.id ? "#22D3EE55" : "#1E293B"}`, borderRadius: 10, padding: "14px 16px", marginBottom: 8, cursor: "pointer", transition: "border-color 0.2s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 9, fontFamily: "monospace", color: "#475569" }}>{r.id}</span>
                      <span style={{ width: 1, height: 10, background: "#1E293B" }} />
                      <span style={{ fontSize: 9, fontFamily: "monospace", color: "#64748B" }}>{r.ward}</span>
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 700, fontFamily: "'Playfair Display', serif", color: "#F1F5F9" }}>{r.type}</div>
                    <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginTop: 3 }}>📍 {r.location}</div>
                    <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", marginTop: 3 }}>👤 {r.reporter} · {r.date}</div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6, flexShrink: 0, marginLeft: 12 }}>
                    <RiskBadge score={r.risk} />
                    <StatusPill status={r.status} />
                  </div>
                </div>

                {selectedReport?.id === r.id && (
                  <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid #1E293B" }}>
                    <div style={{ fontSize: 10, color: "#22D3EE", fontFamily: "monospace", letterSpacing: 2, marginBottom: 10 }}>ADMIN ACTIONS</div>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      {["Assign Team", "Escalate", "Mark Resolved", "Request Info"].map(action => (
                        <button key={action} style={{ padding: "6px 12px", background: "#0F172A", border: "1px solid #1E293B", borderRadius: 6, color: "#94A3B8", fontFamily: "monospace", fontSize: 10, cursor: "pointer" }}
                          onClick={e => e.stopPropagation()}>
                          {action}
                        </button>
                      ))}
                    </div>
                    <div style={{ marginTop: 10, fontSize: 10, fontFamily: "monospace", color: "#475569" }}>
                      LAT: {r.lat.toFixed(4)}° N &nbsp;|&nbsp; LNG: {r.lng.toFixed(4)}° E &nbsp;|&nbsp; PRIORITY: {r.priority}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Heatmap Tab */}
        {activeTab === "heatmap" && (
          <div>
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 4 }}>GIS RISK HEATMAP — HYDERABAD</div>
              <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>Real-time complaint density and severity overlay</div>
            </div>
            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 16, marginBottom: 16 }}>
              <HeatmapCanvas reports={reports} />
              <div style={{ display: "flex", gap: 16, marginTop: 12, flexWrap: "wrap" }}>
                {[["#FF4444", "Critical (80+)"], ["#FF8800", "High (60-79)"], ["#64C8FF", "Medium (<60)"]].map(([c, l]) => (
                  <div key={l} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div style={{ width: 10, height: 10, borderRadius: "50%", background: c }} />
                    <span style={{ fontSize: 10, fontFamily: "monospace", color: "#64748B" }}>{l}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 16 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 12 }}>HOTSPOT ZONES</div>
              {[
                { zone: "Ameerpet Junction", count: 5, avgRisk: 88, trend: "↑ +2 this week" },
                { zone: "Kukatpally HB Colony", count: 4, avgRisk: 79, trend: "↑ +3 this week" },
                { zone: "Madhapur / HITEC", count: 3, avgRisk: 71, trend: "→ Stable" },
              ].map(z => (
                <div key={z.zone} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #1E293B" }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "#F1F5F9", fontFamily: "monospace" }}>{z.zone}</div>
                    <div style={{ fontSize: 10, color: "#64748B", fontFamily: "monospace", marginTop: 2 }}>{z.count} complaints · Avg risk: {z.avgRisk}</div>
                  </div>
                  <span style={{ fontSize: 10, fontFamily: "monospace", color: z.trend.includes("↑") ? "#FF6666" : "#64748B" }}>{z.trend}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div>
            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 18, marginBottom: 14 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 14 }}>ISSUE CATEGORY BREAKDOWN</div>
              {Object.entries(
                reports.reduce((acc, r) => { acc[r.type] = (acc[r.type] || 0) + 1; return acc; }, {})
              ).map(([type, count]) => (
                <div key={type} style={{ marginBottom: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontFamily: "monospace", color: TYPE_COLORS[type] || "#94A3B8" }}>{type}</span>
                    <span style={{ fontSize: 11, fontFamily: "monospace", color: "#64748B" }}>{count}</span>
                  </div>
                  <div style={{ height: 8, background: "#0F172A", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${(count / reports.length) * 100}%`, background: TYPE_COLORS[type] || "#22D3EE", borderRadius: 4 }} />
                  </div>
                </div>
              ))}
            </div>

            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 18, marginBottom: 14 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 14 }}>BUDGET OPTIMIZATION ENGINE</div>
              {[
                { category: "Pothole Repair", allocation: 42, efficiency: 78 },
                { category: "Street Lighting", allocation: 23, efficiency: 91 },
                { category: "Waste Management", allocation: 20, efficiency: 65 },
                { category: "Footpath Repair", allocation: 15, efficiency: 55 },
              ].map(b => (
                <div key={b.category} style={{ marginBottom: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontFamily: "monospace", color: "#94A3B8" }}>{b.category}</span>
                    <span style={{ fontSize: 11, fontFamily: "monospace", color: "#64748B" }}>₹{b.allocation}L · {b.efficiency}% efficient</span>
                  </div>
                  <div style={{ height: 10, background: "#0F172A", borderRadius: 5, overflow: "hidden", position: "relative" }}>
                    <div style={{ height: "100%", width: `${b.allocation}%`, background: `linear-gradient(90deg, #22D3EE, #0EA5E9)`, borderRadius: 5 }} />
                    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${b.efficiency}%`, background: "rgba(16,185,129,0.2)", borderRadius: 5 }} />
                  </div>
                </div>
              ))}
              <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", marginTop: 8 }}>
                💡 AI Recommendation: Reallocate ₹3L from Street Lighting to Waste Management in Madhapur zone
              </div>
            </div>

            <div style={{ background: "#0D1117", border: "1px solid #1E293B", borderRadius: 12, padding: 18 }}>
              <div style={{ fontSize: 10, color: "#94A3B8", fontFamily: "monospace", letterSpacing: 2, marginBottom: 12 }}>MONTHLY RESOLUTION TREND</div>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 80 }}>
                {[42, 55, 38, 67, 71, 58, 80, 63, 75, 88, 72, 91].map((v, i) => (
                  <div key={i} style={{ flex: 1, background: `linear-gradient(to top, #22D3EE, #0EA5E9)`, height: `${v}%`, borderRadius: "3px 3px 0 0", opacity: 0.7 + i * 0.025 }} />
                ))}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6 }}>
                {["M", "A", "M", "J", "J", "A", "S", "O", "N", "D", "J", "F"].map((m, i) => (
                  <div key={i} style={{ fontSize: 8, color: "#475569", fontFamily: "monospace", flex: 1, textAlign: "center" }}>{m}</div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Root App ──────────────────────────────────────────────────────────────
export default function App() {
  const [session, setSession] = useState(null);
  const [reports, setReports] = useState(ISSUES);

  if (!session) return <AuthScreen onAuth={(username, role) => setSession({ username, role })} />;

  if (session.role === "admin") return <AdminDashboard user={session.username} reports={reports} onLogout={() => setSession(null)} />;

  return <CitizenDashboard user={session.username} reports={reports} onNewReport={r => setReports(p => [r, ...p])} onLogout={() => setSession(null)} />;
}