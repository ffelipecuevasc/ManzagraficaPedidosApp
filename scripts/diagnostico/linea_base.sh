#!/usr/bin/env bash
# =====================================================================
# Linea base de produccion - Iteracion 00-01 (consola Bash de PythonAnywhere)
# SOLO LECTURA: no escribe, no borra, no abre el contenido de los respaldos.
# Solo usa du, find, date, awk, python --version, pip freeze y diff.
#
# Como usarlo: abre una consola Bash nueva, pega este archivo completo y
# pulsa Enter. Antes de pegarlo, cambia las dos lineas PROYECTO y VENV.
# Todo el codigo vive dentro de una funcion para que un error de rutas no
# cierre la consola. Pasos exactos y formato de respuesta: evidencia-00-01.md.
#
# Sin tildes a proposito: el archivo se pega en una consola cuya
# codificacion no controlamos.
# =====================================================================

# --- Edita estas dos lineas (PENDIENTE_DESARROLLADOR: rutas reales) ---
# PROYECTO: carpeta del proyecto en el servidor (la que tiene manage.py).
# VENV: carpeta del entorno virtual de la web app (pestana Web > Virtualenv).
PROYECTO="${PROYECTO:-PENDIENTE_DESARROLLADOR}"
VENV="${VENV:-PENDIENTE_DESARROLLADOR}"

linea_base_produccion() {
    if [ ! -f "$PROYECTO/manage.py" ] || [ ! -x "$VENV/bin/python" ]; then
        echo "ERROR: revisa PROYECTO y VENV. Debe existir \$PROYECTO/manage.py y \$VENV/bin/python."
        echo "PROYECTO=$PROYECTO"
        echo "VENV=$VENV"
        return 2
    fi

    echo "=== [A] Fecha de la medicion ==="
    date -u '+%Y-%m-%d %H:%M:%S UTC'

    echo
    echo "=== [B] Disco de la cuenta (archivos; no incluye la base MySQL) ==="
    echo "MB por carpeta de primer nivel de \$HOME; la fila mas grande es el total."
    echo "Compara con los 512 MiB del plan y con el indicador de disco del Dashboard."
    du -m --max-depth=1 "$HOME" 2>/dev/null | sort -rn | head -12

    echo
    echo "=== [C] Carpeta backups/ (solo metadatos: fecha y tamano) ==="
    local dir_backups="$PROYECTO/backups"
    if [ -d "$dir_backups" ]; then
        local lista
        lista=$(find "$dir_backups" -maxdepth 1 -type f -printf '%T@ %TY-%Tm-%Td %TH:%TM %s %f\n' 2>/dev/null | sort -n)
        if [ -z "$lista" ]; then
            echo "Volcados: 0 archivos"
        else
            echo "Fecha y hora del servidor   Tamano (bytes)   Archivo"
            echo "$lista" | awk '{ printf "%s %s   %14d   %s\n", $2, $3, $4, $5 }'
            echo
            echo "$lista" | awk -v ahora="$(date +%s)" '
                NR == 1 { minimo = $1 }
                { n++; total += $4; maximo = $1 }
                END {
                    printf "Volcados: %d archivos\n", n
                    printf "Tamano total: %.2f MB\n", total / 1048576
                    printf "Antiguedad del mas antiguo: %.1f dias\n", (ahora - minimo) / 86400
                    printf "Antiguedad del mas reciente: %.1f dias\n", (ahora - maximo) / 86400
                }'
        fi
        echo "Subcarpetas dentro de backups/ (MB y nombre):"
        find "$dir_backups" -mindepth 1 -maxdepth 1 -type d -exec du -sm {} + 2>/dev/null
        echo "Tamano de backups/ completo (MB): $(du -sm "$dir_backups" | cut -f1)"
    else
        echo "No existe $dir_backups"
    fi

    echo
    echo "=== [D] Carpeta media/ ==="
    if [ -d "$PROYECTO/media" ]; then
        echo "Tamano (MB): $(du -sm "$PROYECTO/media" | cut -f1)"
        echo "Archivos: $(find "$PROYECTO/media" -type f | wc -l)"
    else
        echo "No existe $PROYECTO/media"
    fi

    echo
    echo "=== [E] Python del entorno de la web app ==="
    "$VENV/bin/python" --version 2>&1

    echo
    echo "=== [F] pip freeze frente a requirements.txt ==="
    local req="$PROYECTO/requirements.txt"
    if [ ! -f "$req" ]; then
        echo "No existe $req"
    else
        local requeridos instalados
        local bom
        bom=$(head -c 2 "$req" | od -An -tx1 | tr -d ' \n')
        if [ "$bom" = "fffe" ] || [ "$bom" = "feff" ]; then
            echo "(requirements.txt esta en UTF-16: se convierte solo para comparar)"
            requeridos=$(iconv -f UTF-16 -t UTF-8 "$req" 2>/dev/null)
        else
            requeridos=$(cat "$req")
        fi
        instalados=$("$VENV/bin/pip" freeze 2>/dev/null)
        requeridos=$(echo "$requeridos" | tr -d '\r' | sed 's/^\xef\xbb\xbf//' | sed '/^[[:space:]]*$/d' | tr 'A-Z' 'a-z' | sort)
        instalados=$(echo "$instalados" | tr -d '\r' | sed '/^[[:space:]]*$/d' | tr 'A-Z' 'a-z' | sort)
        echo "Paquetes en requirements.txt: $(echo "$requeridos" | sed '/^$/d' | wc -l)"
        echo "Paquetes instalados en el entorno: $(echo "$instalados" | sed '/^$/d' | wc -l)"
        local diferencias
        diferencias=$(diff <(echo "$requeridos") <(echo "$instalados"))
        if [ -z "$diferencias" ]; then
            echo "Sin diferencias entre requirements.txt y pip freeze."
        else
            echo "Diferencias ( < solo en requirements.txt   > solo instalado en el entorno ):"
            echo "$diferencias"
        fi
    fi

    echo
    echo "=== Fin de la medicion ==="
}

linea_base_produccion
