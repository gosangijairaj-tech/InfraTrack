import streamlit.components.v1 as components

GPS_HTML = """
<style>
  body{margin:0;font-family:'Segoe UI',sans-serif}
  #btn{background:#0077B6;color:#fff;border:none;padding:10px 18px;
       border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;width:100%}
  #btn:hover{background:#005f8e}
  #btn:disabled{background:#94a3b8;cursor:not-allowed}
  #st{margin-top:8px;font-size:12px;padding:6px 10px;border-radius:6px;display:none}
  .ok{background:#d1fae5;color:#065f46}
  .er{background:#fee2e2;color:#991b1b}
  .ld{background:#dbeafe;color:#1e40af}
</style>
<button id="btn" onclick="go()">📡 Capture GPS Location</button>
<div id="st"></div>
<script>
function go(){
  const btn=document.getElementById('btn'),st=document.getElementById('st');
  if(!navigator.geolocation){
    st.textContent='❌ Geolocation not supported by your browser.';
    st.className='er';st.style.display='block';return;
  }
  btn.disabled=true;btn.textContent='⏳ Acquiring GPS…';
  st.textContent='Requesting location from device…';st.className='ld';st.style.display='block';
  navigator.geolocation.getCurrentPosition(
    p=>{
      const lat=p.coords.latitude.toFixed(6),
            lon=p.coords.longitude.toFixed(6),
            acc=Math.round(p.coords.accuracy);
      st.textContent=`✅ Lat: ${lat}  Lon: ${lon}  (±${acc} m accuracy)`;
      st.className='ok';
      btn.textContent='✅ GPS Captured';
      window.parent.postMessage(
        {type:'streamlit:setComponentValue',
         value:JSON.stringify({lat:parseFloat(lat),lon:parseFloat(lon),accuracy:acc})},
        '*'
      );
    },
    e=>{
      const msgs={1:'Permission denied — allow location in browser settings.',
                  2:'Position unavailable. Check GPS/Wi-Fi.',
                  3:'Timed out. Try again.'};
      st.textContent='❌ '+(msgs[e.code]||'Unknown error');
      st.className='er';btn.disabled=false;btn.textContent='📡 Capture GPS Location';
    },
    {enableHighAccuracy:true,timeout:12000,maximumAge:0}
  );
}
</script>
"""


def render_gps_button() -> dict | None:
    result = components.html(GPS_HTML, height=90)
    if result and isinstance(result, str):
        import json
        try:
            return json.loads(result)
        except Exception:
            pass
    return None