"""Small dependency-free SVG figures for auditable notebook evidence."""
import html

def lines(title, labels, series, ylabel='USDT'):
    palette=['#173e38','#b56732','#647985','#8163a0'];width,height=880,350
    values=[float(v) for values in series.values() for v in values];low=min(values+[0]);high=max(values+[0]);span=high-low or 1
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><g font-family="Arial" font-size="12" fill="#243b35"><text x="15" y="23" font-size="17">{html.escape(title)}</text><text x="15" y="44">{html.escape(ylabel)}</text>']
    for i in range(5):
        y=270-i*50;v=low+span*i/4;svg.append(f'<path d="M90 {y}H855" stroke="#dde3df"/><text x="5" y="{y+4}">{v:,.2f}</text>')
    for j,(name,ys) in enumerate(series.items()):
        pts=' '.join(f'{90+i*760/max(1,len(ys)-1):.2f},{270-(float(v)-low)*200/span:.2f}' for i,v in enumerate(ys))
        color=palette[j%len(palette)];svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/><text x="{90+j*190}" y="330" fill="{color}">{html.escape(name)}</text>')
    for i in sorted({0,len(labels)//2,len(labels)-1}):
        svg.append(f'<text x="{90+i*720/max(1,len(labels)-1):.1f}" y="295">{html.escape(str(labels[i]))}</text>')
    return ''.join(svg)+'</g></svg>'

def bars(title,labels,values,ylabel='Count'):
    high=max(max(values),0);low=min(min(values),0);span=high-low or 1;zero=270-200*(0-low)/span
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="360"><rect width="100%" height="100%" fill="white"/><g font-family="Arial" font-size="12" fill="#243b35"><text x="15" y="23" font-size="17">{html.escape(title)}</text><text x="15" y="45">{html.escape(ylabel)}</text><path d="M80 {zero}H860" stroke="#80938b"/>']
    for i,(label,value) in enumerate(zip(labels,values)):
        x=90+i*760/len(values);y=270-(value-low)*200/span;h=abs(y-zero)
        out.append(f'<rect x="{x}" y="{min(y,zero)}" width="{min(85,600/len(values))}" height="{max(.5,h)}" fill="#416c5c"/><text x="{x}" y="{min(y,zero)-8}">{value:,.2f}</text><text x="{x}" y="310">{html.escape(str(label))}</text>')
    return ''.join(out)+'</g></svg>'

def table(headers,rows):
    def cell(v):return html.escape(str(v))
    return {'text/html':'<table style="border-collapse:collapse;font:14px Arial"><thead><tr>'+''.join('<th style="padding:8px;border-bottom:2px solid #385064;text-align:left">'+cell(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td style="padding:8px;border-bottom:1px solid #dde3df">'+cell(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'}
def figure(svg):
    import hashlib,base64
    from pathlib import Path
    cached=Path(__file__).resolve().parents[1]/'artifacts/review/figures'/(hashlib.sha256(svg.encode()).hexdigest()+'.png')
    if cached.exists():return {'image/png':base64.b64encode(cached.read_bytes()).decode()}
    return {'image/svg+xml':svg}

