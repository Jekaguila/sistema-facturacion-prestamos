# Guía de Git y GitHub para este proyecto

## Primera vez (en tu computadora)

```bash
git config --global user.name  "Tu Nombre"
git config --global user.email "tu_correo@ejemplo.com"
```

## Clonar o iniciar

```bash
# Opción A: tomar este repositorio como base (descomprime el .zip y entra a la carpeta)
cd sistema-facturacion-prestamos
git log --oneline            # historial de ejemplo

# Opción B: partir de cero
git init
```

## Flujo de trabajo diario (ramas pequeñas + commits pequeños)

```bash
git switch -c feature/repositorio-json     # 1. rama por cada reto
# ... editas código ...
python -m pytest && ruff check .           # 2. pruebas y estilo ANTES de commitear
git add src/prestamos/almacenes.py tests/  # 3. agrega solo lo que corresponde
git commit -m "feat: agrega RepositorioJSON con pruebas"
git switch main
git merge feature/repositorio-json
```

## Mensajes de commit (convención sugerida)

| Prefijo | Cuándo |
|---|---|
| `feat:` | funcionalidad nueva |
| `fix:` | corrección de error |
| `test:` | agrega o mejora pruebas |
| `refactor:` | mejora el diseño sin cambiar el comportamiento |
| `docs:` | documentación |

Un buen mensaje responde **qué** cambió y **por qué**, en una línea de menos de 72 caracteres.

## Publicar en GitHub

1. En GitHub: **New repository** → nombre `sistema-facturacion-prestamos` → *sin* README ni .gitignore (ya existen).
2. En tu terminal:

```bash
git remote add origin https://github.com/<tu-usuario>/sistema-facturacion-prestamos.git
git branch -M main
git push -u origin main
```

3. Verifica en la web que se vean: `README.md`, `src/`, `tests/`, `docs/` y el historial de commits.
4. Copia el enlace del repositorio y pégalo **en el foro, junto con el código**: no basta con dejar un enlace.

## Errores frecuentes

- **Subir `.venv/` o `__pycache__/`** → ya están en `.gitignore`; no los fuerces con `git add -f`.
- **Un solo commit gigante** → el historial es evidencia de tu proceso; haz commits por avance.
- **Commitear con pruebas fallando** → corre `python -m pytest` antes.
- **Empujar claves o contraseñas** → nunca las guardes en el código.
