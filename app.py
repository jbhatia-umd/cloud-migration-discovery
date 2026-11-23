"""Interactive, fictional cloud-migration pre-sales demo."""
import csv
import io
import json
from dataclasses import asdict

import streamlit as st
from estimator import Scenario, evaluate

st.set_page_config(page_title='CloudPath | Discovery & ROI', page_icon='☁️', layout='wide')
st.title('☁️ CloudPath | Migration Discovery & ROI')
st.caption('Portfolio proof-of-concept • Synthetic example • Not a provider price quote')
st.info('All assumptions are editable. This tool does not connect to AWS, Azure, a DMS, or customer records.')

with st.sidebar:
    st.header('1 · Customer discovery')
    company = st.text_input('Organization', 'Example Legal Group (fictional)')
    users = st.number_input('Employees / users', min_value=1, value=45)
    storage_tb = st.number_input('Document storage (TB)', min_value=0.1, value=8.0, step=0.5)
    environment = st.selectbox('Current environment', ['Legacy document management system', 'On-premises file server', 'Mixed cloud and on-premises'])
    priorities = st.multiselect('Customer priorities', ['Lower monthly spend', 'Security', 'Migration simplicity', 'Business continuity', 'Scalability', 'Data retention'], default=['Lower monthly spend','Migration simplicity'])
    st.header('2 · Current spending')
    current_storage = st.number_input('Storage/vendor cost per month ($)', min_value=0.0, value=2300.0, step=100.0)
    current_admin = st.number_input('IT/admin cost per month ($)', min_value=0.0, value=700.0, step=100.0)
    st.header('3 · Proposed spending (assumptions)')
    per_gb = st.number_input('Storage cost per GB-month ($)', min_value=0.0, value=0.023, format='%.4f')
    new_admin = st.number_input('Admin cost per month ($)', min_value=0.0, value=450.0, step=50.0)
    licenses = st.number_input('Software/license cost per month ($)', min_value=0.0, value=600.0, step=50.0)
    migration = st.number_input('One-time migration project ($)', min_value=0.0, value=7000.0, step=500.0)
    contingency = st.slider('Migration contingency (%)', 0, 100, 15)
    growth = st.slider('Annual storage growth (%)', -50, 100, 10)

scenario = Scenario(company, int(users), storage_tb, current_storage, current_admin,
                    per_gb, new_admin, licenses, migration, float(contingency), float(growth))
r = evaluate(scenario)
cols = st.columns(4)
cols[0].metric('Current monthly cost', f"${r['current_monthly']:,.0f}")
cols[1].metric('Proposed monthly cost', f"${r['proposed_monthly']:,.0f}")
cols[2].metric('Year-one savings / (extra cost)', f"${r['first_year_difference']:,.0f}")
cols[3].metric('Estimated payback', f"{r['payback_months']} mo" if r['payback_months'] is not None else 'Not achieved')

st.subheader('Cost comparison')
st.bar_chart({'Current monthly': r['current_monthly'], 'Proposed monthly': r['proposed_monthly']})
st.caption('Includes no change in current baseline costs and no future license price changes. Year-one calculation includes a one-time migration charge and contingency.')

st.subheader('Customer-facing recommendation')
st.write(r['recommendation'])
st.markdown(f"**Discovery context:** {company} has **{users} users**, **{storage_tb:.1f} TB** of documents, and a **{environment.lower()}**. Priorities: {', '.join(priorities) if priorities else 'Not selected'}.")

st.subheader('Solution concept (not deployed)')
st.code('Users → Identity / SSO → Document application → Object storage\n                           ↘ Audit logging / monitoring\nMigration: inventory → pilot → validation → phased cutover', language='text')
st.markdown('**Validation items before making a real recommendation:** retention/legal hold, permissions, encryption and key management, recovery objectives, API/DMS compatibility, bandwidth, data egress, migration downtime, compliance and vendor licensing.')

with st.expander('Show pricing math and limitations'):
    st.markdown('**Proposed monthly** = storage TB × 1,024 GB/TB × assumed $/GB-month + admin + licenses.  **Year-one delta** = 12 × (current monthly − proposed monthly) − migration × (1 + contingency).  **Payback** = migration including contingency ÷ monthly recurring savings, only when savings are positive.')
    st.warning('Illustrative synthetic pricing only. This model excludes requests, API calls, data transfer, redundancy, backup, support, taxes, vendor-specific DMS costs and compliance controls. Verify with official pricing calculators before proposing any real deal.')

payload = {'scenario': asdict(scenario), 'results': r, 'priorities': priorities, 'environment': environment, 'disclaimer': 'Synthetic scenario; unverified pricing assumptions.'}
st.download_button('Download customer scenario (JSON)', json.dumps(payload, indent=2), file_name='cloudpath_discovery.json', mime='application/json')
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(['Metric', 'Value'])
for k, v in r.items():
    writer.writerow([k, v])
st.download_button('Download cost summary (CSV)', output.getvalue(), file_name='cloudpath_roi.csv', mime='text/csv')
