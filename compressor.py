#!/usr/bin/env python3
from PIL import Image
import os
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

class Compressor:
    def __init__(self, qualidade: int, resize: float = None):
        self.qualidade = qualidade
        self.resize = resize  # Fator de redimensionamento entre 0 e 1 ou None

    def comprimir_imagem(self, caminho_entrada: str, caminho_saida: str):
        if not os.path.exists(caminho_saida):
            os.makedirs(caminho_saida)
        try:
            with Image.open(caminho_entrada) as img:
                if self.resize:
                    largura_original, altura_original = img.size
                    nova_largura = int(largura_original * self.resize)
                    nova_altura = int(altura_original * self.resize)
                    img = img.resize((nova_largura, nova_altura))
                    console.print(f"[yellow]Imagem redimensionada para {nova_largura}x{nova_altura}[/yellow]")
                nome_arquivo = os.path.basename(caminho_entrada)
                caminho_saida_completo = os.path.join(caminho_saida, os.path.splitext(nome_arquivo)[0] + '.webp')
                img.save(caminho_saida_completo, 'WEBP', quality=self.qualidade)
                tamanho_original = os.path.getsize(caminho_entrada)
                tamanho_comprimido = os.path.getsize(caminho_saida_completo)
                compressao = 100 * (tamanho_original - tamanho_comprimido) / tamanho_original
                tamanho_original_kb = tamanho_original / 1024
                tamanho_comprimido_kb = tamanho_comprimido / 1024
            return {
                "caminho_original": caminho_entrada,
                "tamanho_original_kb": tamanho_original_kb,
                "caminho_saida": caminho_saida_completo,
                "tamanho_comprimido_kb": tamanho_comprimido_kb,
                "compressao": compressao
            }
        except Exception as e:
            console.print(f"[red]Erro ao comprimir a imagem: {e}[/red]")
            sys.exit(1)

def compress(args):
    caminho_entrada = os.path.abspath(args.input)
    qualidade = args.qualidade
    resize = args.resize
    compressor = Compressor(qualidade, resize)
    resultados = []

    if resize is not None:
        if not (0 < resize <= 1):
            console.print('[red]O fator de redimensionamento deve estar entre 0 e 1![/red]')
            sys.exit(1)

    if not os.path.exists(caminho_entrada):
        console.print('[red]Arquivo de entrada ou pasta não encontrada![/red]')
        sys.exit(1)

    tabela = Table(title="Detalhes da Compressão")
    tabela.add_column("Caminho Original", style="cyan", overflow="fold")
    tabela.add_column("Tamanho Original (KB)", style="magenta", justify="right")
    tabela.add_column("Tamanho Comprimido (KB)", style="magenta", justify="right")
    tabela.add_column("Economia (%)", style="green", justify="right")

    with Live(tabela, refresh_per_second=4, console=console):
        if os.path.isdir(caminho_entrada):
            arquivos = [f for f in os.listdir(caminho_entrada) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for arquivo in arquivos:
                caminho_comprimir = os.path.join(caminho_entrada, arquivo)
                caminho_saida = os.path.abspath(args.output) if args.output else caminho_entrada
                resultado = compressor.comprimir_imagem(caminho_comprimir, caminho_saida)
                if resultado:
                    tabela.add_row(
                        resultado["caminho_original"],
                        f"{resultado['tamanho_original_kb']:.2f}",
                        f"{resultado['tamanho_comprimido_kb']:.2f}",
                        f"[red]{resultado['compressao']:.2f}%[/red]" if resultado["compressao"] < 0 else f"{resultado['compressao']:.2f}%"
                    )
        else:
            resultado = compressor.comprimir_imagem(caminho_entrada, args.output)
            if resultado:
                tabela.add_row(
                    resultado["caminho_original"],
                    f"{resultado['tamanho_original_kb']:.2f}",
                    f"{resultado['tamanho_comprimido_kb']:.2f}",
                    f"[red]{resultado['compressao']:.2f}%[/red]" if resultado["compressao"] < 0 else f"{resultado['compressao']:.2f}%"
                )
        resultados.append(resultado)

def main():
    parser = argparse.ArgumentParser(description="Compressor de Imagens")
    parser.add_argument('input', type=str, default='.',help="Caminho da imagem ou pasta de entrada")
    parser.add_argument('output', type=str, nargs='?', default='.', help="Diretório de saída")
    parser.add_argument('-q', '--qualidade', type=int, default=80, help="Qualidade da compressão")
    parser.add_argument('-r', '--resize', type=float, default=None, help="Fator de redimensionamento entre 0 e 1")
    args = parser.parse_args()
    compress(args)

if __name__ == "__main__":
    main()
