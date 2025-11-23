# Inicia el entorno de desarrollo (local, frontend, o backend)
set dotenv-path := ".webapp"
layer-list := "project-webapp deploy-terraform"

dev ENV:
    #!/usr/bin/env sh
    case "{{ENV}}" in
        local)
            cd local && just up;;
        frontend)
            cd frontend && pnpm install && pnpm dev;;
        deploy)
            echo "Deploy no implementado";;
        *)
            echo "Entorno no reconocido. Usa: local, frontend, o deploy";;
    esac

add-layer layer_name:
    #!/usr/bin/env sh
    echo "Adding layer ${layer_name} to project from local templates..."
    template_dir="${WEBAPP_TEMPLATES_DIR}/${layer_name}"
    answers_file=".copier-answers.${layer_name}.yml";
    echo "  ${layer_name} : ${answers_file} | ${template_dir}"
    if [ ! -d "${template_dir}" ]; then
        echo "Local template dir not found: ${template_dir}"
        exit 1
    fi
    pipx run copier copy ${template_dir} .

[confirm("This will delete and recreate project layers from local templates. Are you sure? (y/N)")]
recopy:
    #!/usr/bin/env sh
    echo "Recopying templates from local locations..."
    for layer_name in {{layer-list}}; do
        template_dir="${WEBAPP_TEMPLATES_DIR}/${layer_name}";
        answers_file=".copier-answers.${layer_name}.yml";
        echo "  ${layer_name} : ${answers_file} | ${template_dir}";
        if [ ! -d "${template_dir}" ]; then
            echo "Local template dir not found: ${template_dir}";
            exit 1
        fi
        if [ -f "$answers_file" ]; then
            pipx run copier recopy --skip-answered --vcs-ref HEAD --answers-file "$answers_file" .
        else
            pipx run copier copy --vcs-ref HEAD ${template_dir} .
        fi
    done

list-layers:
    #!/usr/bin/env sh
    echo "Layers installed:"
    for layer_name in {{layer-list}}; do
        answers_file=".copier-answers.${layer_name}.yml";
        if [ -f "$answers_file" ]; then
            echo "${layer_name}: installed"
        else
            echo "${layer_name}: not installed"
        fi
    done

# Construir la imagen Docker del backend
team-build:
    #!/usr/bin/env sh
    echo "🔨 Construyendo imagen Docker del backend..."
    docker build -f Dockerfile.backend -t backend:latest .
    echo "✅ Build completado"

# Iniciar los servicios con docker-compose
up:
    #!/usr/bin/env sh
    cd local && docker-compose up -d

# Detener los servicios
down:
    #!/usr/bin/env sh
    cd local && docker-compose down

# Ver logs de los servicios
logs:
    #!/usr/bin/env sh
    cd local && docker-compose logs -f