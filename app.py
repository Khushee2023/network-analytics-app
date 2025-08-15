from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
from collections import Counter
import os

app = Flask(__name__)

def load_network_data():
    """Load network data from CSV file"""
    try:
        # Try to load the CSV file
        df = pd.read_csv('network_data.csv')
        return df
    except FileNotFoundError:
        print("Error: network_data.csv file not found!")
        return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def compute_stats(df):
    """Compute network statistics"""
    if df is None:
        return None
    
    stats = {}
    
    # Count packets per protocol
    protocol_counts = df['Protocol'].value_counts().to_dict()
    stats['protocol_counts'] = protocol_counts
    
    # Find top 3 talking IPs (by packet count)
    # Combine source and destination IPs
    all_ips = list(df['Source IP']) + list(df['Destination IP'])
    ip_counter = Counter(all_ips)
    top_ips = dict(ip_counter.most_common(3))
    stats['top_ips'] = top_ips
    
    # Total packets
    stats['total_packets'] = len(df)
    
    # Average packet size
    stats['avg_packet_size'] = df['Packet Size'].mean()
    
    return stats

def create_protocol_chart(protocol_counts):
    """Create a bar chart for protocol distribution"""
    plt.figure(figsize=(10, 6))
    protocols = list(protocol_counts.keys())
    counts = list(protocol_counts.values())
    
    bars = plt.bar(protocols, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.title('Packet Count by Protocol', fontsize=16, fontweight='bold')
    plt.xlabel('Protocol', fontsize=12)
    plt.ylabel('Number of Packets', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_ip_chart(top_ips):
    """Create a pie chart for top talking IPs"""
    plt.figure(figsize=(10, 8))
    ips = list(top_ips.keys())
    counts = list(top_ips.values())
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    wedges, texts, autotexts = plt.pie(counts, labels=ips, autopct='%1.1f%%', 
                                       colors=colors, startangle=90)
    
    plt.title('Top 3 Most Active IPs', fontsize=16, fontweight='bold')
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.axis('equal')
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route('/')
def dashboard():
    """Main dashboard route"""
    # Load data
    df = load_network_data()
    
    if df is None:
        return render_template('error.html', 
                             error_message="Could not load network_data.csv file. Please make sure it exists in the project directory.")
    
    # Compute statistics
    stats = compute_stats(df)
    
    # Create charts
    protocol_chart = create_protocol_chart(stats['protocol_counts'])
    ip_chart = create_ip_chart(stats['top_ips'])
    
    return render_template('dashboard.html', 
                         stats=stats,
                         protocol_chart=protocol_chart,
                         ip_chart=ip_chart)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    df = load_network_data()
    if df is None:
        return jsonify({'error': 'Could not load data'})
    
    stats = compute_stats(df)
    return jsonify(stats)

if __name__ == '__main__':
    print("Starting Flask Network Analytics App...")
    print("Make sure 'network_data.csv' is in the same directory as this script!")
    app.run(debug=True, host='0.0.0.0', port=5000)