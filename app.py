import streamlit as st
import pandas as pd

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer

from sklearn.cluster import KMeans


import numpy as np

# 리눅스 일때 
import platform
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
plt.rcParams['axes.unicode_minus'] = False
if platform.system() == 'Linux':
    rc('font', family='NanumGothic')


def main() :
    st.title('K-Means 클러스터링 앱')
    st.text('CSV 파일을 업로드하면, 비슷한 유형의 데이터끼리 묶어주는 앱입니다')

    # 1. csv 파일 업로드
    file = st.file_uploader('csv파일 업로드', type=['csv'])

    if file is not None :
        
        # 1-1. 판다스의 데이터프레임으로 읽는다.
        df = pd.read_csv(file, index_col=1)

        # 1-2. 10개 미만의 파일을 올리면, 에러 처리하자
        if df.shape[0] < 10 :
            st.error('데이터의 갯수는 10개 이상이어야 합니다.')
            return

        # 1-3. 유저한테 데이터프레임 보여준다.
        st.dataframe(df)
        
        # 2. nan 데이터 있으면, 삭제하자.
        print( df.isna().sum() )

        st.subheader('각 컬럼별 Nan의 갯수 입니다.')

        st.dataframe( df.isna().sum() )

        df.dropna(inplace=True)

        # dropna 하면 reset_index 를 해줘야 한다
        df.reset_index(inplace=True)

        st.info('Nan 이 있으면 해당 데이터는 삭제합니다.')

        # 3. 유저한테 컬럼을 선택 할 수 있도록 하자.
        print( df.columns )

        st.subheader('클러스터링에 사용 할 컬럼을 선택합니다.')

        selected_columns = st.multiselect('X로 사용 할 컬럼을 선택하세요.', df.columns)

        X = df[ selected_columns ]

        if selected_columns == [] :
            pass
        else :
            st.dataframe( X )

        # 밑에 있는 것을 하려면 유저가 2개 이상 선택을 해야한다
        if len(selected_columns) >= 2 : 
            
            X_new = pd.DataFrame()

            print(X_new)

            # 4. 해당 컬럼의 데이터가 문자열이면, 숫자로 바꿔주자.

            for  column  in X.columns :
                
                print( X[column].dtype )

                # 컬럼의 데이터가 문자열이면, 레이블인코딩 또는 원핫인코딩 해야한다.
                if X[column].dtype == object :
                    if X[column].nunique() >= 3 :
                        # 원핫인코딩
                        column_names = sorted( X[column].unique() )
                        # 비어있는 데이터프레임에 컬럼 추가
                        X_new[column_names] = pd.get_dummies( X[column].to_frame() )
                        
                    else :
                        # 레이블인코딩
                        encoder = LabelEncoder()
                        X_new[column]= encoder.fit_transform( X[column] )

                else :
                    # 숫자 데이터 처리
                    X_new[column] = X[column]
                
            # X_new 변수가 숫자로만 되어있는 데이터프레임.
            # 4-1. 유저한테 보여주자.

            X_new.reset_index(inplace=True, drop=True)

            st.subheader('클러스터링에 실제 사용 할 데이터')
            st.dataframe(X_new)

            # 5. K의 갯수를 1개부터 10개까지 해서 wcss를 구한다.
            wcss = []
            for k in np.arange(1, 10+1) :
                kmeans = KMeans(n_clusters=k, random_state=5)
                kmeans.fit(X_new)
                wcss.append(kmeans.inertia_)
                
            # 6. elobw method 를 이용해서. 차트로 보여준다.
            fig1 = plt.figure()
            x = np.arange(1, 10+1)
            plt.plot(x, wcss)
            plt.title('엘보우 메소드')
            plt.xlabel('클러스터의 갯수')
            plt.ylabel('WCSS')
            st.pyplot(fig1)

            # 7. 유저가 k의 갯수를 정한다.
            k = st.slider('클러스터 갯수 설정', min_value=1, max_value=10)

            # 8. KMeans 수행해서 그룹정보를 가져온다.
            kmeans = KMeans(n_clusters= k, random_state= 5)
            y_pred = kmeans.fit_predict(X_new)
            
            # 9. 원래 있던 df 에 Group 이라는컬럼을 만들어준다.
            df['Group'] = y_pred

            # 10. 결과를 파일로 저장한다.
            df.to_csv('result.csv')

            # 11. 유저한테 보여준다.
            st.subheader('클러스터링 결과')

            st.dataframe(df)

            # 12. 유저가 그룹을 선택하면, 해당 그룹의 정보를 보여준다.
            choice = st.selectbox('그룹을 선택하세요', np.arange(0, k))

            st.dataframe(df.loc[ df['Group'] == choice , ])

        elif len(selected_columns) <= 1 :
            st.write('컬럼을 2개 이상 선택해 주세요.')
    else : 
        pass

if __name__ == '__main__' :
    main()