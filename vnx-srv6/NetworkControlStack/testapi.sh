#!/usr/bin/env bash

# Configuración base
BASE_URL="http://138.4.21.11:32500"  # Ajustar según tu configuración
# BASE_URL="http://your-service-ip:5000"  # Para Kubernetes

echo "=== PROBANDO CONTROLADOR DE FLUJOS ==="

# 1. Health Check
echo -e "\n🏥 1. Health Check"
curl -s -X GET "$BASE_URL/health" -w "\nStatus: %{http_code}\n"

# 2. Ver estado inicial de los flujos
echo -e "\n📋 2. Listar flujos iniciales"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 3. Crear flujo sin ruta (requiere recálculo automático)
echo -e "\n➕ 3. Crear flujo SIN ruta (fd00:0:2::1)"
curl -s -X POST "$BASE_URL/flows/fd00%3A0%3A2%3A%3A1" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nStatus: %{http_code}\n"

# 4. Crear flujo con ruta específica
echo -e "\n➕ 4. Crear flujo CON ruta (fd00:0:2::2)"
curl -s -X POST "$BASE_URL/flows/fd00%3A0%3A2%3A%3A2" \
  -H "Content-Type: application/json" \
  -d '{"route":["ru","r1","r3","rg"]}' \
  -w "\nStatus: %{http_code}\n"

# 5. Crear otro flujo con ruta diferente
echo -e "\n➕ 5. Crear flujo CON ruta alternativa (fd00:0:3::2)"
curl -s -X POST "$BASE_URL/flows/fd00%3A0%3A3%3A%3A2" \
  -H "Content-Type: application/json" \
  -d '{"route":["ru","r2","r4","rc"]}' \
  -w "\nStatus: %{http_code}\n"

# 6. Intentar crear flujo duplicado (debe fallar)
echo -e "\n❌ 6. Intentar crear flujo duplicado (debe fallar con 409)"
curl -s -X POST "$BASE_URL/flows/fd00%3A0%3A2%3A%3A1" \
  -H "Content-Type: application/json" \
  -d '{"route":["ru","r7","r8","rg"]}' \
  -w "\nStatus: %{http_code}\n"

# 7. Ver todos los flujos después de las creaciones
echo -e "\n📋 7. Listar todos los flujos después de creaciones"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# Esperar un momento para que el PCE procese
echo -e "\n⏰ Esperando 2 segundos para que el PCE procese..."
sleep 2

# 7.1 Ver flujos después del procesamiento del PCE
echo -e "\n📋 7.1 Listar flujos después del procesamiento del PCE"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 8. Actualizar ruta de un flujo existente
echo -e "\n🔄 8. Actualizar ruta del flujo fd00:0:2::2"
curl -s -X PUT "$BASE_URL/flows/fd00%3A0%3A2%3A%3A2" \
  -H "Content-Type: application/json" \
  -d '{"route":["ru","r1","r4","r7","rg"]}' \
  -w "\nStatus: %{http_code}\n"

# 9. Intentar actualizar flujo inexistente
echo -e "\n❌ 9. Intentar actualizar flujo inexistente (debe fallar con 404)"
curl -s -X PUT "$BASE_URL/flows/fd00%3A0%3A2%3A%3A999" \
  -H "Content-Type: application/json" \
  -d '{"route":["ru","r1","r2","rg"]}' \
  -w "\nStatus: %{http_code}\n"

# 10. Ver flujos después de la actualización
echo -e "\n📋 10. Listar flujos después de actualización"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 11. Eliminar un flujo
echo -e "\n🗑️ 11. Eliminar flujo fd00:0:2::1"
curl -s -X DELETE "$BASE_URL/flows/fd00%3A0%3A2%3A%3A1" \
  -w "\nStatus: %{http_code}\n"

# 12. Intentar eliminar flujo inexistente
echo -e "\n❌ 12. Intentar eliminar flujo inexistente (debe retornar 404)"
curl -s -X DELETE "$BASE_URL/flows/fd00%3A0%3A2%3A%3A999" \
  -w "\nStatus: %{http_code}\n"

# 13. Ver flujos finales
echo -e "\n📋 13. Listar flujos después de eliminaciones"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 14. Verificar estado de los locks (debugging)
echo -e "\n🔒 14. Verificar estado de locks"
curl -s -X GET "$BASE_URL/locks/status" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 15. Limpiar - eliminar flujos restantes
echo -e "\n🧹 15. Limpiar flujos restantes"
echo "Eliminando fd00:0:2::2..."
curl -s -X DELETE "$BASE_URL/flows/fd00%3A0%3A2%3A%3A2" \
  -w "\nStatus: %{http_code}\n"

echo "Eliminando fd00:0:3::1 (si existe)..."
curl -s -X DELETE "$BASE_URL/flows/fd00%3A0%3A3%3A%3A1" \
  -w "\nStatus: %{http_code}\n"

echo "Eliminando fd00:0:3::2..."
curl -s -X DELETE "$BASE_URL/flows/fd00%3A0%3A3%3A%3A2" \
  -w "\nStatus: %{http_code}\n"

# 16. Verificar limpieza final
echo -e "\n📋 16. Verificar limpieza final"
curl -s -X GET "$BASE_URL/flows" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\n"

echo -e "\n✅ PRUEBAS COMPLETADAS"