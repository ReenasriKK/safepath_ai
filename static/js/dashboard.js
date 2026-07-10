// Lightweight JS for dashboard animations and Chart placeholders
document.addEventListener('DOMContentLoaded', function(){
  // Add pulse animation to stat cards
  document.querySelectorAll('.stat-card').forEach((el,i)=>{
    setTimeout(()=> el.classList.add('pulse'), 200*i);
  });

  // Initialize Chart.js charts if present
  if(window.Chart){
    try{
      const ctx = document.getElementById('hazardBarChart');
      if(ctx){
        const labels = window.hazardLabels && window.hazardLabels.length ? window.hazardLabels : ['Pothole','Flood','Construction','Garbage'];
        const data = window.hazardCounts && window.hazardCounts.length ? window.hazardCounts : [5,2,3,8];
        const colors = ['#6c5ce7','#00d2ff','#00b894','#fdcb6e','#ff7675','#0984e3','#6ab04c'];
        new Chart(ctx, {
          type: 'bar',
          data: {labels:labels, datasets:[{label:'Detections',data:data, backgroundColor: labels.map((_,i)=>colors[i % colors.length])}]},
          options:{responsive:true,plugins:{legend:{display:false}}}
        });
      }

      // Weekly line chart if present
      const weekly = document.getElementById('weeklyLineChart');
      if(weekly){
        const wLabels = window.weekLabels || [];
        const wData = window.weekCounts || [];
        new Chart(weekly, {type:'line', data:{labels:wLabels, datasets:[{label:'Detections', data:wData, borderColor:'#00d2ff', backgroundColor:'rgba(0,210,255,0.08)', fill:true}]}, options:{responsive:true}});
      }
    }catch(e){console.warn('Chart init failed',e)}
  }
});
