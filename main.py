import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd
from datetime import datetime
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

os.environ['GOOGLE_API_KEY']='AIzaSyDkQsTLQe3Y6lHyFzy5Yq_Nr7tJaq2Zdjg'

load_dotenv()

st.set_page_config(page_title='Pós Venda',layout='wide')

mes_dict={1:'JANEIRO',2:'FEVEREIRO',3:'MARÇO',4:'ABRIL',5:'MAIO',6:'JUNHO',7:'JULHO',8:'AGOSTO',9:'SETEMBRO',10:'OUTUBRO',11:'NOVEMBRO',12:'DEZEMBRO'}

class Dash:

    def __init__(self) -> None:

        self.url='https://docs.google.com/spreadsheets/d/1JwUHULZfwLiJMUMtPePlB2vFZY1NaUbzzJNRqqovFl8/edit?usp=sharing'

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )

        self.template="""

        você é um analista de atendimento e tem como objetivo identificar padrão de melhorias e de performace com base nas informações apresentadas abaixo:

        {tabela}

        E com base nisso me dar insights aonde preciso melhorar minha atuação com o cliente.

        """

        self.prompt=PromptTemplate.from_template(self.template)
        self.parser=StrOutputParser()

        self.chain=self.prompt|self.llm|self.parser

        pass

    def main(self):

        placeholder=st.empty()

        dt_now=datetime(year=datetime.now().year,month=12,day=31)
        dt_inic=datetime(year=datetime.now().year,month=1,day=1)

        var_dict=dict()

        with placeholder.container():

            st.title('Pós Venda')
            st.subheader('Pesquisa de satisfação')
            st.markdown('----')

            with st.sidebar:

                st.subheader('Menu')
                st.markdown('----')
                var_dict['dt_inicial']=st.date_input(label='Data inicial',value=dt_inic)
                var_dict['dt_final']=st.date_input(label='Data Final',value=dt_now)

                btn_refresh=st.button('Atualizar',type='primary',use_container_width=True)

                pass
            
            df=self.gsSheet()

            df['Carimbo de data/hora']=df['Carimbo de data/hora'].apply(self.formatarData)
            df['Ano']=df['Carimbo de data/hora'].dt.year
            df['ID Mês']=df['Carimbo de data/hora'].dt.month
            df['Mês']=df['Carimbo de data/hora'].dt.month.apply(lambda info: mes_dict[info])
            df['Dia']=df['Carimbo de data/hora'].dt.day

            df=df.loc[df['Carimbo de data/hora'].between(dt_inic,dt_now)]

            div1,div2=st.columns(2)

            with div1.container():

                title='Como você avaliaria a qualidade da chamada com o vendedor(a)?'
                col_dict={title:'Status','Carimbo de data/hora':'Avaliação'}

                temp_df=df.groupby([title],as_index=False).agg({'Carimbo de data/hora':'count'})
                temp_df.rename(columns=col_dict,inplace=True)
                
                bar=px.pie(temp_df,values='Avaliação',names='Status')
                st.caption(title)
                st.plotly_chart(bar,use_container_width=True)

                title='Como você avaliaria o atendimento do entregador(a)?'
                col_dict={title:'Status','Carimbo de data/hora':'Avaliação'}

                temp_df=df.groupby([title],as_index=False).agg({'Carimbo de data/hora':'count'})
                temp_df.rename(columns=col_dict,inplace=True)
                
                bar=px.pie(temp_df,values='Avaliação',names='Status')
                st.caption(title)
                st.plotly_chart(bar,use_container_width=True)                

                pass


            with div2.container():

                title='Como você avaliaria a qualidade da entrega?'
                col_dict={title:'Status','Carimbo de data/hora':'Avaliação'}

                temp_df=df.groupby([title],as_index=False).agg({'Carimbo de data/hora':'count'})
                temp_df.rename(columns=col_dict,inplace=True)
                
                bar=px.pie(temp_df,values='Avaliação',names='Status')
                st.caption(title)
                st.plotly_chart(bar,use_container_width=True)

                title='Como você avaliaria a qualidade do produto que recebeu?'
                col_dict={title:'Status','Carimbo de data/hora':'Avaliação'}

                temp_df=df.groupby([title],as_index=False).agg({'Carimbo de data/hora':'count'})
                temp_df.rename(columns=col_dict,inplace=True)
                
                bar=px.pie(temp_df,values='Avaliação',names='Status')
                st.caption(title)
                st.plotly_chart(bar,use_container_width=True)                

                pass

            
            st.title('Insights')
            st.markdown('----')
            response=self.chain.invoke(df)
            st.caption(response)

            temp_df=df.groupby(['ID Mês','Mês'],as_index=False).agg({'Carimbo de data/hora':'count'})
            temp_df.rename(columns={'Carimbo de data/hora':'Avaliação'},inplace=True)
            bar=px.bar(temp_df,x='Mês',y='Avaliação',title='Avaliação Mensal',text_auto=True)
            bar.update_traces(textfont_size=12,textangle=0,textposition='outside',cliponaxis=False)

            st.plotly_chart(bar,use_container_width=True)

            st.dataframe(df,use_container_width=True,hide_index=True)

            pass

        if btn_refresh:

            st.rerun()

            pass

        pass


    def gsSheet(self):

        conn=st.connection('gsheets',type=GSheetsConnection)

        data=conn.read(spreadsheet=self.url)
        return data

        pass

    def formatarData(self,val):

        val=str(val)

        val=val.split()[0]
        val=val.split('/')

        val=datetime(year=int(val[-1]),month=int(val[1]),day=int(val[0]))

        return val

        pass

    pass


app=Dash()
app.main()