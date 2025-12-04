"""
Script de Análise Estatística - Experimento GraphQL vs REST
Sprint 2 - Laboratório de Experimentação de Software

Este script realiza análise estatística completa dos dados coletados,
respondendo às perguntas de pesquisa RQ1 e RQ2.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import mannwhitneyu, shapiro, levene
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class ExperimentAnalyzer:
    
    def __init__(self, data_file: str, output_dir: str = "results"):
        self.data_file = data_file
        self.output_dir = output_dir
        self.df = None
        self.results = {}
        
        os.makedirs(output_dir, exist_ok=True)
        
        self._load_data()
    
    def _load_data(self):
        print("\n" + "=" * 70)
        print("CARREGANDO DADOS DO EXPERIMENTO")
        print("=" * 70)
        
        self.df = pd.read_csv(self.data_file)
        
        initial_count = len(self.df)
        self.df = self.df[self.df['success'] == True].copy()
        success_count = len(self.df)
        
        print(f"\n✓ Dados carregados: {self.data_file}")
        print(f"  - Total de medições: {initial_count}")
        print(f"  - Medições bem-sucedidas: {success_count}")
        print(f"  - Medições com erro: {initial_count - success_count}")
        
        print("\n" + "-" * 70)
        print("DISTRIBUIÇÃO DAS MEDIÇÕES")
        print("-" * 70)
        print(self.df.groupby(['api_type', 'query_type']).size().unstack(fill_value=0))
    
    def descriptive_statistics(self):
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS DESCRITIVAS")
        print("=" * 70)
        
        stats_df = self.df.groupby(['api_type', 'query_type']).agg({
            'response_time_ms': ['count', 'mean', 'std', 'min', 'median', 'max'],
            'response_size_bytes': ['mean', 'std', 'min', 'median', 'max']
        }).round(2)
        
        print("\n" + "-" * 70)
        print("TEMPO DE RESPOSTA (ms)")
        print("-" * 70)
        print(stats_df['response_time_ms'])
        
        print("\n" + "-" * 70)
        print("TAMANHO DA RESPOSTA (bytes)")
        print("-" * 70)
        print(stats_df['response_size_bytes'])
        
        stats_df.to_csv(os.path.join(self.output_dir, 'descriptive_statistics.csv'))
        print(f"\n✓ Estatísticas descritivas salvas em: {self.output_dir}/descriptive_statistics.csv")
        
        return stats_df
    
    def check_normality(self):
        print("\n" + "=" * 70)
        print("TESTE DE NORMALIDADE (Shapiro-Wilk)")
        print("=" * 70)
        print("H0: Os dados seguem distribuição normal")
        print("α = 0.05")
        
        normality_results = []
        
        for api_type in ['REST', 'GraphQL']:
            for query_type in self.df['query_type'].unique():
                for metric in ['response_time_ms', 'response_size_bytes']:
                    data = self.df[(self.df['api_type'] == api_type) & 
                                   (self.df['query_type'] == query_type)][metric]
                    
                    if len(data) >= 3:
                        stat, p_value = shapiro(data)
                        is_normal = p_value > 0.05
                        
                        normality_results.append({
                            'api_type': api_type,
                            'query_type': query_type,
                            'metric': metric,
                            'statistic': stat,
                            'p_value': p_value,
                            'is_normal': is_normal
                        })
        
        normality_df = pd.DataFrame(normality_results)
        
        print("\n" + "-" * 70)
        print("RESULTADOS DO TESTE DE NORMALIDADE")
        print("-" * 70)
        print(normality_df.to_string(index=False))
        
        normal_count = normality_df['is_normal'].sum()
        total_count = len(normality_df)
        print(f"\n✓ Grupos com distribuição normal: {normal_count}/{total_count}")
        
        if normal_count < total_count:
            print("⚠ Alguns grupos não seguem distribuição normal.")
            print("  Recomendação: Usar testes não-paramétricos (Mann-Whitney U)")
        
        normality_df.to_csv(os.path.join(self.output_dir, 'normality_test.csv'), index=False)
        
        self.results['normality'] = normality_df
        return normality_df
    
    def check_variance_homogeneity(self):
        print("\n" + "=" * 70)
        print("TESTE DE HOMOGENEIDADE DE VARIÂNCIAS (Levene)")
        print("=" * 70)
        print("H0: As variâncias são homogêneas entre os grupos")
        print("α = 0.05")
        
        levene_results = []
        
        for query_type in self.df['query_type'].unique():
            for metric in ['response_time_ms', 'response_size_bytes']:
                rest_data = self.df[(self.df['api_type'] == 'REST') & 
                                    (self.df['query_type'] == query_type)][metric]
                graphql_data = self.df[(self.df['api_type'] == 'GraphQL') & 
                                       (self.df['query_type'] == query_type)][metric]
                
                if len(rest_data) > 0 and len(graphql_data) > 0:
                    stat, p_value = levene(rest_data, graphql_data)
                    is_homogeneous = p_value > 0.05
                    
                    levene_results.append({
                        'query_type': query_type,
                        'metric': metric,
                        'statistic': stat,
                        'p_value': p_value,
                        'is_homogeneous': is_homogeneous
                    })
        
        levene_df = pd.DataFrame(levene_results)
        
        print("\n" + "-" * 70)
        print("RESULTADOS DO TESTE DE LEVENE")
        print("-" * 70)
        print(levene_df.to_string(index=False))
        
        levene_df.to_csv(os.path.join(self.output_dir, 'levene_test.csv'), index=False)
        
        self.results['levene'] = levene_df
        return levene_df
    
    def rq1_analysis(self):
        print("\n" + "=" * 70)
        print("RQ1: ANÁLISE DE TEMPO DE RESPOSTA")
        print("=" * 70)
        print("H0: μ_GraphQL = μ_REST (não há diferença)")
        print("H1: μ_GraphQL < μ_REST (GraphQL é mais rápido)")
        print("α = 0.05")
        
        rq1_results = []
        
        print("\n" + "-" * 70)
        print("ANÁLISE GERAL (Todos os tipos de consulta)")
        print("-" * 70)
        
        rest_times = self.df[self.df['api_type'] == 'REST']['response_time_ms']
        graphql_times = self.df[self.df['api_type'] == 'GraphQL']['response_time_ms']
        
        t_stat, t_pvalue = stats.ttest_ind(graphql_times, rest_times, alternative='less')
        
        u_stat, u_pvalue = mannwhitneyu(graphql_times, rest_times, alternative='less')
        
        cohens_d = (graphql_times.mean() - rest_times.mean()) / np.sqrt(
            ((len(graphql_times) - 1) * graphql_times.std()**2 + 
             (len(rest_times) - 1) * rest_times.std()**2) / 
            (len(graphql_times) + len(rest_times) - 2)
        )
        
        print(f"\nREST - Tempo médio: {rest_times.mean():.2f} ms (DP: {rest_times.std():.2f})")
        print(f"GraphQL - Tempo médio: {graphql_times.mean():.2f} ms (DP: {graphql_times.std():.2f})")
        print(f"Diferença: {rest_times.mean() - graphql_times.mean():.2f} ms")
        print(f"\nTeste t: t = {t_stat:.4f}, p-value = {t_pvalue:.4f}")
        print(f"Mann-Whitney U: U = {u_stat:.4f}, p-value = {u_pvalue:.4f}")
        print(f"Cohen's d: {cohens_d:.4f}")
        
        if u_pvalue < 0.05:
            print("\n✓ RESULTADO: GraphQL é significativamente mais rápido que REST (p < 0.05)")
        else:
            print("\n✗ RESULTADO: Não há diferença significativa (p >= 0.05)")
        
        rq1_results.append({
            'query_type': 'GERAL',
            'rest_mean': rest_times.mean(),
            'rest_std': rest_times.std(),
            'graphql_mean': graphql_times.mean(),
            'graphql_std': graphql_times.std(),
            'difference': rest_times.mean() - graphql_times.mean(),
            't_statistic': t_stat,
            't_pvalue': t_pvalue,
            'u_statistic': u_stat,
            'u_pvalue': u_pvalue,
            'cohens_d': cohens_d,
            'significant': u_pvalue < 0.05
        })
        
        print("\n" + "-" * 70)
        print("ANÁLISE POR TIPO DE CONSULTA")
        print("-" * 70)
        
        for query_type in sorted(self.df['query_type'].unique()):
            print(f"\n{query_type.upper()}:")
            
            rest_times = self.df[(self.df['api_type'] == 'REST') & 
                                 (self.df['query_type'] == query_type)]['response_time_ms']
            graphql_times = self.df[(self.df['api_type'] == 'GraphQL') & 
                                    (self.df['query_type'] == query_type)]['response_time_ms']
            
            if len(rest_times) > 0 and len(graphql_times) > 0:
                t_stat, t_pvalue = stats.ttest_ind(graphql_times, rest_times, alternative='less')
                u_stat, u_pvalue = mannwhitneyu(graphql_times, rest_times, alternative='less')
                
                cohens_d = (graphql_times.mean() - rest_times.mean()) / np.sqrt(
                    ((len(graphql_times) - 1) * graphql_times.std()**2 + 
                     (len(rest_times) - 1) * rest_times.std()**2) / 
                    (len(graphql_times) + len(rest_times) - 2)
                )
                
                print(f"  REST: {rest_times.mean():.2f} ms (DP: {rest_times.std():.2f})")
                print(f"  GraphQL: {graphql_times.mean():.2f} ms (DP: {graphql_times.std():.2f})")
                print(f"  Diferença: {rest_times.mean() - graphql_times.mean():.2f} ms")
                print(f"  Mann-Whitney U: p-value = {u_pvalue:.4f}")
                
                if u_pvalue < 0.05:
                    print(f"  ✓ GraphQL significativamente mais rápido")
                else:
                    print(f"  ✗ Sem diferença significativa")
                
                rq1_results.append({
                    'query_type': query_type,
                    'rest_mean': rest_times.mean(),
                    'rest_std': rest_times.std(),
                    'graphql_mean': graphql_times.mean(),
                    'graphql_std': graphql_times.std(),
                    'difference': rest_times.mean() - graphql_times.mean(),
                    't_statistic': t_stat,
                    't_pvalue': t_pvalue,
                    'u_statistic': u_stat,
                    'u_pvalue': u_pvalue,
                    'cohens_d': cohens_d,
                    'significant': u_pvalue < 0.05
                })
        
        rq1_df = pd.DataFrame(rq1_results)
        rq1_df.to_csv(os.path.join(self.output_dir, 'rq1_analysis.csv'), index=False)
        print(f"\n✓ Resultados RQ1 salvos em: {self.output_dir}/rq1_analysis.csv")
        
        self.results['rq1'] = rq1_df
        return rq1_df
    
    def rq2_analysis(self):
        print("\n" + "=" * 70)
        print("RQ2: ANÁLISE DE TAMANHO DA RESPOSTA")
        print("=" * 70)
        print("H0: μ_GraphQL = μ_REST (não há diferença)")
        print("H1: μ_GraphQL < μ_REST (GraphQL tem respostas menores)")
        print("α = 0.05")
        
        rq2_results = []
        
        print("\n" + "-" * 70)
        print("ANÁLISE GERAL (Todos os tipos de consulta)")
        print("-" * 70)
        
        rest_sizes = self.df[self.df['api_type'] == 'REST']['response_size_bytes']
        graphql_sizes = self.df[self.df['api_type'] == 'GraphQL']['response_size_bytes']
        
        t_stat, t_pvalue = stats.ttest_ind(graphql_sizes, rest_sizes, alternative='less')
        u_stat, u_pvalue = mannwhitneyu(graphql_sizes, rest_sizes, alternative='less')
        
        cohens_d = (graphql_sizes.mean() - rest_sizes.mean()) / np.sqrt(
            ((len(graphql_sizes) - 1) * graphql_sizes.std()**2 + 
             (len(rest_sizes) - 1) * rest_sizes.std()**2) / 
            (len(graphql_sizes) + len(rest_sizes) - 2)
        )
        
        print(f"\nREST - Tamanho médio: {rest_sizes.mean():.2f} bytes (DP: {rest_sizes.std():.2f})")
        print(f"GraphQL - Tamanho médio: {graphql_sizes.mean():.2f} bytes (DP: {graphql_sizes.std():.2f})")
        print(f"Diferença: {rest_sizes.mean() - graphql_sizes.mean():.2f} bytes")
        print(f"Redução percentual: {((rest_sizes.mean() - graphql_sizes.mean()) / rest_sizes.mean() * 100):.2f}%")
        print(f"\nTeste t: t = {t_stat:.4f}, p-value = {t_pvalue:.4f}")
        print(f"Mann-Whitney U: U = {u_stat:.4f}, p-value = {u_pvalue:.4f}")
        print(f"Cohen's d: {cohens_d:.4f}")
        
        if u_pvalue < 0.05:
            print("\n✓ RESULTADO: GraphQL tem respostas significativamente menores (p < 0.05)")
        else:
            print("\n✗ RESULTADO: Não há diferença significativa (p >= 0.05)")
        
        rq2_results.append({
            'query_type': 'GERAL',
            'rest_mean': rest_sizes.mean(),
            'rest_std': rest_sizes.std(),
            'graphql_mean': graphql_sizes.mean(),
            'graphql_std': graphql_sizes.std(),
            'difference': rest_sizes.mean() - graphql_sizes.mean(),
            'reduction_percent': (rest_sizes.mean() - graphql_sizes.mean()) / rest_sizes.mean() * 100,
            't_statistic': t_stat,
            't_pvalue': t_pvalue,
            'u_statistic': u_stat,
            'u_pvalue': u_pvalue,
            'cohens_d': cohens_d,
            'significant': u_pvalue < 0.05
        })
        
        print("\n" + "-" * 70)
        print("ANÁLISE POR TIPO DE CONSULTA")
        print("-" * 70)
        
        for query_type in sorted(self.df['query_type'].unique()):
            print(f"\n{query_type.upper()}:")
            
            rest_sizes = self.df[(self.df['api_type'] == 'REST') & 
                                 (self.df['query_type'] == query_type)]['response_size_bytes']
            graphql_sizes = self.df[(self.df['api_type'] == 'GraphQL') & 
                                    (self.df['query_type'] == query_type)]['response_size_bytes']
            
            if len(rest_sizes) > 0 and len(graphql_sizes) > 0:
                t_stat, t_pvalue = stats.ttest_ind(graphql_sizes, rest_sizes, alternative='less')
                u_stat, u_pvalue = mannwhitneyu(graphql_sizes, rest_sizes, alternative='less')
                
                cohens_d = (graphql_sizes.mean() - rest_sizes.mean()) / np.sqrt(
                    ((len(graphql_sizes) - 1) * graphql_sizes.std()**2 + 
                     (len(rest_sizes) - 1) * rest_sizes.std()**2) / 
                    (len(graphql_sizes) + len(rest_sizes) - 2)
                )
                
                reduction = (rest_sizes.mean() - graphql_sizes.mean()) / rest_sizes.mean() * 100
                
                print(f"  REST: {rest_sizes.mean():.2f} bytes (DP: {rest_sizes.std():.2f})")
                print(f"  GraphQL: {graphql_sizes.mean():.2f} bytes (DP: {graphql_sizes.std():.2f})")
                print(f"  Diferença: {rest_sizes.mean() - graphql_sizes.mean():.2f} bytes")
                print(f"  Redução: {reduction:.2f}%")
                print(f"  Mann-Whitney U: p-value = {u_pvalue:.4f}")
                
                if u_pvalue < 0.05:
                    print(f"  ✓ GraphQL significativamente menor")
                else:
                    print(f"  ✗ Sem diferença significativa")
                
                rq2_results.append({
                    'query_type': query_type,
                    'rest_mean': rest_sizes.mean(),
                    'rest_std': rest_sizes.std(),
                    'graphql_mean': graphql_sizes.mean(),
                    'graphql_std': graphql_sizes.std(),
                    'difference': rest_sizes.mean() - graphql_sizes.mean(),
                    'reduction_percent': reduction,
                    't_statistic': t_stat,
                    't_pvalue': t_pvalue,
                    'u_statistic': u_stat,
                    'u_pvalue': u_pvalue,
                    'cohens_d': cohens_d,
                    'significant': u_pvalue < 0.05
                })
        
        rq2_df = pd.DataFrame(rq2_results)
        rq2_df.to_csv(os.path.join(self.output_dir, 'rq2_analysis.csv'), index=False)
        print(f"\n✓ Resultados RQ2 salvos em: {self.output_dir}/rq2_analysis.csv")
        
        self.results['rq2'] = rq2_df
        return rq2_df
    
    def anova_analysis(self):
        print("\n" + "=" * 70)
        print("ANOVA BIDIRECIONAL")
        print("=" * 70)
        print("Análise de interação: Tipo de API × Tipo de Consulta")
        
        anova_results = {}
        
        print("\n" + "-" * 70)
        print("TEMPO DE RESPOSTA")
        print("-" * 70)
        
        model_time = ols('response_time_ms ~ C(api_type) + C(query_type) + C(api_type):C(query_type)', 
                         data=self.df).fit()
        anova_time = sm.stats.anova_lm(model_time, typ=2)
        print(anova_time)
        
        anova_results['time'] = anova_time
        
        print("\n" + "-" * 70)
        print("TAMANHO DA RESPOSTA")
        print("-" * 70)
        
        model_size = ols('response_size_bytes ~ C(api_type) + C(query_type) + C(api_type):C(query_type)', 
                         data=self.df).fit()
        anova_size = sm.stats.anova_lm(model_size, typ=2)
        print(anova_size)
        
        anova_results['size'] = anova_size
        
        anova_time.to_csv(os.path.join(self.output_dir, 'anova_time.csv'))
        anova_size.to_csv(os.path.join(self.output_dir, 'anova_size.csv'))
        
        self.results['anova'] = anova_results
        return anova_results
    
    def create_visualizations(self):
        print("\n" + "=" * 70)
        print("GERANDO VISUALIZAÇÕES")
        print("=" * 70)
        
        viz_dir = os.path.join(self.output_dir, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        sns.boxplot(data=self.df, x='query_type', y='response_time_ms', hue='api_type')
        plt.title('Tempo de Resposta por Tipo de Consulta', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de Consulta', fontsize=12)
        plt.ylabel('Tempo de Resposta (ms)', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='API', loc='upper right')
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        sns.boxplot(data=self.df, x='api_type', y='response_time_ms')
        plt.title('Tempo de Resposta Geral', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de API', fontsize=12)
        plt.ylabel('Tempo de Resposta (ms)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'boxplot_response_time.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Salvo: boxplot_response_time.png")
        plt.close()
        
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        sns.boxplot(data=self.df, x='query_type', y='response_size_bytes', hue='api_type')
        plt.title('Tamanho da Resposta por Tipo de Consulta', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de Consulta', fontsize=12)
        plt.ylabel('Tamanho da Resposta (bytes)', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='API', loc='upper right')
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        sns.boxplot(data=self.df, x='api_type', y='response_size_bytes')
        plt.title('Tamanho da Resposta Geral', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de API', fontsize=12)
        plt.ylabel('Tamanho da Resposta (bytes)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'boxplot_response_size.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Salvo: boxplot_response_size.png")
        plt.close()
        
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        time_means = self.df.groupby(['api_type', 'query_type'])['response_time_ms'].agg(['mean', 'sem']).reset_index()
        
        x = np.arange(len(time_means['query_type'].unique()))
        width = 0.35
        
        rest_data = time_means[time_means['api_type'] == 'REST']
        graphql_data = time_means[time_means['api_type'] == 'GraphQL']
        
        plt.bar(x - width/2, rest_data['mean'], width, yerr=rest_data['sem']*1.96, 
                label='REST', capsize=5, alpha=0.8)
        plt.bar(x + width/2, graphql_data['mean'], width, yerr=graphql_data['sem']*1.96, 
                label='GraphQL', capsize=5, alpha=0.8)
        
        plt.xlabel('Tipo de Consulta', fontsize=12)
        plt.ylabel('Tempo Médio de Resposta (ms)', fontsize=12)
        plt.title('Comparação de Tempo de Resposta (IC 95%)', fontsize=14, fontweight='bold')
        plt.xticks(x, rest_data['query_type'], rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        size_means = self.df.groupby(['api_type', 'query_type'])['response_size_bytes'].agg(['mean', 'sem']).reset_index()
        
        rest_data = size_means[size_means['api_type'] == 'REST']
        graphql_data = size_means[size_means['api_type'] == 'GraphQL']
        
        plt.bar(x - width/2, rest_data['mean'], width, yerr=rest_data['sem']*1.96, 
                label='REST', capsize=5, alpha=0.8)
        plt.bar(x + width/2, graphql_data['mean'], width, yerr=graphql_data['sem']*1.96, 
                label='GraphQL', capsize=5, alpha=0.8)
        
        plt.xlabel('Tipo de Consulta', fontsize=12)
        plt.ylabel('Tamanho Médio da Resposta (bytes)', fontsize=12)
        plt.title('Comparação de Tamanho da Resposta (IC 95%)', fontsize=14, fontweight='bold')
        plt.xticks(x, rest_data['query_type'], rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'barplot_comparison.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Salvo: barplot_comparison.png")
        plt.close()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        axes[0, 0].hist(self.df[self.df['api_type'] == 'REST']['response_time_ms'], 
                        bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_title('Distribuição - Tempo REST', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Tempo de Resposta (ms)')
        axes[0, 0].set_ylabel('Frequência')
        axes[0, 0].grid(alpha=0.3)
        
        axes[0, 1].hist(self.df[self.df['api_type'] == 'GraphQL']['response_time_ms'], 
                        bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_title('Distribuição - Tempo GraphQL', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Tempo de Resposta (ms)')
        axes[0, 1].set_ylabel('Frequência')
        axes[0, 1].grid(alpha=0.3)
        
        axes[1, 0].hist(self.df[self.df['api_type'] == 'REST']['response_size_bytes'], 
                        bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[1, 0].set_title('Distribuição - Tamanho REST', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Tamanho da Resposta (bytes)')
        axes[1, 0].set_ylabel('Frequência')
        axes[1, 0].grid(alpha=0.3)
        
        axes[1, 1].hist(self.df[self.df['api_type'] == 'GraphQL']['response_size_bytes'], 
                        bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[1, 1].set_title('Distribuição - Tamanho GraphQL', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Tamanho da Resposta (bytes)')
        axes[1, 1].set_ylabel('Frequência')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'histograms_distribution.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Salvo: histograms_distribution.png")
        plt.close()
        
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        sns.violinplot(data=self.df, x='api_type', y='response_time_ms', inner='box')
        plt.title('Distribuição do Tempo de Resposta', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de API', fontsize=12)
        plt.ylabel('Tempo de Resposta (ms)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        sns.violinplot(data=self.df, x='api_type', y='response_size_bytes', inner='box')
        plt.title('Distribuição do Tamanho da Resposta', fontsize=14, fontweight='bold')
        plt.xlabel('Tipo de API', fontsize=12)
        plt.ylabel('Tamanho da Resposta (bytes)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'violinplot_distributions.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Salvo: violinplot_distributions.png")
        plt.close()
        
        print(f"\n✓ Todas as visualizações salvas em: {viz_dir}/")
    
    def generate_summary_report(self):
        print("\n" + "=" * 70)
        print("GERANDO RELATÓRIO RESUMIDO")
        print("=" * 70)
        
        report_file = os.path.join(self.output_dir, 'analysis_summary.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("RELATÓRIO DE ANÁLISE ESTATÍSTICA\n")
            f.write("Experimento: GraphQL vs REST\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Data da Análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Arquivo de Dados: {self.data_file}\n")
            f.write(f"Total de Medições Analisadas: {len(self.df)}\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("RQ1: TEMPO DE RESPOSTA\n")
            f.write("=" * 70 + "\n\n")
            
            if 'rq1' in self.results:
                rq1_general = self.results['rq1'][self.results['rq1']['query_type'] == 'GERAL'].iloc[0]
                
                f.write(f"REST - Tempo médio: {rq1_general['rest_mean']:.2f} ms\n")
                f.write(f"GraphQL - Tempo médio: {rq1_general['graphql_mean']:.2f} ms\n")
                f.write(f"Diferença: {rq1_general['difference']:.2f} ms\n")
                f.write(f"Mann-Whitney U p-value: {rq1_general['u_pvalue']:.4f}\n")
                f.write(f"Cohen's d: {rq1_general['cohens_d']:.4f}\n\n")
                
                if rq1_general['significant']:
                    f.write("CONCLUSÃO: GraphQL apresenta tempo de resposta significativamente\n")
                    f.write("menor que REST (p < 0.05). A hipótese alternativa H1 é aceita.\n")
                else:
                    f.write("CONCLUSÃO: Não há diferença estatisticamente significativa no tempo\n")
                    f.write("de resposta entre GraphQL e REST (p >= 0.05). H0 não pode ser rejeitada.\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("RQ2: TAMANHO DA RESPOSTA\n")
            f.write("=" * 70 + "\n\n")
            
            if 'rq2' in self.results:
                rq2_general = self.results['rq2'][self.results['rq2']['query_type'] == 'GERAL'].iloc[0]
                
                f.write(f"REST - Tamanho médio: {rq2_general['rest_mean']:.2f} bytes\n")
                f.write(f"GraphQL - Tamanho médio: {rq2_general['graphql_mean']:.2f} bytes\n")
                f.write(f"Diferença: {rq2_general['difference']:.2f} bytes\n")
                f.write(f"Redução percentual: {rq2_general['reduction_percent']:.2f}%\n")
                f.write(f"Mann-Whitney U p-value: {rq2_general['u_pvalue']:.4f}\n")
                f.write(f"Cohen's d: {rq2_general['cohens_d']:.4f}\n\n")
                
                if rq2_general['significant']:
                    f.write("CONCLUSÃO: GraphQL apresenta tamanho de resposta significativamente\n")
                    f.write("menor que REST (p < 0.05). A hipótese alternativa H2 é aceita.\n")
                else:
                    f.write("CONCLUSÃO: Não há diferença estatisticamente significativa no tamanho\n")
                    f.write("da resposta entre GraphQL e REST (p >= 0.05). H0 não pode ser rejeitada.\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("Arquivos gerados:\n")
            f.write("  - descriptive_statistics.csv\n")
            f.write("  - normality_test.csv\n")
            f.write("  - levene_test.csv\n")
            f.write("  - rq1_analysis.csv\n")
            f.write("  - rq2_analysis.csv\n")
            f.write("  - anova_time.csv\n")
            f.write("  - anova_size.csv\n")
            f.write("  - visualizations/ (diretório com gráficos)\n")
            f.write("=" * 70 + "\n")
        
        print(f"✓ Relatório resumido salvo em: {report_file}")
    
    def run_full_analysis(self):
        print("\n" + "=" * 70)
        print("INICIANDO ANÁLISE ESTATÍSTICA COMPLETA")
        print("=" * 70)
        
        start_time = datetime.now()
        
        self.descriptive_statistics()
        self.check_normality()
        self.check_variance_homogeneity()
        self.rq1_analysis()
        self.rq2_analysis()
        self.anova_analysis()
        self.create_visualizations()
        self.generate_summary_report()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print(f"Duração: {duration:.2f} segundos")
        print(f"Resultados salvos em: {self.output_dir}/")
        print("=" * 70)


def main():
    import sys
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        import glob
        csv_files = glob.glob('results/experiment_*.csv')
        if not csv_files:
            print("ERRO: Nenhum arquivo de dados encontrado!")
            print("Execute o experimento primeiro: python experiment.py")
            sys.exit(1)
        
        data_file = max(csv_files, key=os.path.getmtime)
        print(f"\n✓ Usando arquivo de dados mais recente: {data_file}")
    
    analyzer = ExperimentAnalyzer(data_file)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()

