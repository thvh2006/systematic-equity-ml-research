#!/usr/bin/env python3
"""Apply review formatting and guard editable scenario inputs. Recalculate afterwards."""
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Alignment,Font
from openpyxl.worksheet.datavalidation import DataValidation
R=Path(__file__).resolve().parents[1]
def main():
 p=R/'deliverables/P2_Systematic_Equity_Research.xlsx';w=load_workbook(p)
 for name in ['Read Me','Sources','Paper Monitor']:
  s=w[name];s.column_dimensions['A'].width=30;s.column_dimensions['B'].width=100
  for row in s.iter_rows(min_row=2):
   row[1].alignment=Alignment(wrap_text=True,vertical='top');s.row_dimensions[row[0].row].height=45 if len(str(row[1].value))>80 else 27
 for name,columns in [('Signal Snapshot',[5]),('Month End Holdings',[4]),('Attribution',[4]),('Drawdowns',list(range(2,7)))]:
  for row in w[name].iter_rows(min_row=2):
   for col in columns:row[col-1].number_format='0.00%'
 for row in w['Attribution'].iter_rows(min_row=2):row[2].number_format='#,##0.00;[Red](#,##0.00)'
 s=w['Execution Lab']
 for cells,op,low,high,prompt in [('B2','greaterThan','0',None,'Capital must be positive.'),('B3:B4','greaterThanOrEqual','0',None,'Cost assumptions must be nonnegative.'),('B5','between','0.000000001','1','Participation must be above zero and at most one.')]:
  v=DataValidation(type='decimal',operator=op,formula1=low,formula2=high,allow_blank=False);v.errorTitle='Invalid scenario input';v.error=prompt;v.showErrorMessage=True;v.errorStyle='stop';s.add_data_validation(v);v.add(cells)
 for row in range(2,6):s.cell(row,2).font=Font(color='0066CC',bold=True)
 s['B5'].number_format='0.00%';s['B2'].number_format='#,##0.00'
 for row in [19,20,21]:s.cell(row,2).number_format='#,##0.000000'
 w.save(p);print('Applied wrapping, percentage/currency formats and three input-validation rules; cached formulas require recalculation.')
if __name__=='__main__':main()
