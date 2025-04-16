using System;
using System.Data.SqlClient;
using System.Threading;

class Programa
{
    // Cambia esta cadena de conexión según tu servidor
    static string conexion = "Server=localhost;Database=SistemaFacturas;Trusted_Connection=True;";
    static SemaphoreSlim semaforoImpresion = new SemaphoreSlim(1);

    static void Main()
    {
        for (int i = 1; i <= 3; i++)
        {
            int idAsesor = i;
            Thread hilo = new Thread(() => ImprimirFactura(idAsesor));
            hilo.Start();
        }
    }

    static void ImprimirFactura(int idAsesor)
    {
        while (true)
        {
            semaforoImpresion.Wait();

            int idFactura = 0;
            string numeroFactura = "";

            using (SqlConnection conn = new SqlConnection(conexion))
            {
                conn.Open();

                // Obtener la primera factura no impresa
                string query = "SELECT TOP 1 Id, NumeroFactura FROM Facturas WHERE EstadoImpresion = 0 ORDER BY Id";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                using (SqlDataReader reader = cmd.ExecuteReader())
                {
                    if (reader.Read())
                    {
                        idFactura = reader.GetInt32(0);
                        numeroFactura = reader.GetString(1);
                    }
                    else
                    {
                        Console.WriteLine($"Asesor {idAsesor}: No hay más facturas por imprimir.");
                        semaforoImpresion.Release();
                        break;
                    }
                }

                // Marcar la factura como impresa
                string update = "UPDATE Facturas SET EstadoImpresion = 1 WHERE Id = @Id";
                using (SqlCommand cmd = new SqlCommand(update, conn))
                {
                    cmd.Parameters.AddWithValue("@Id", idFactura);
                    cmd.ExecuteNonQuery();
                }
            }

            semaforoImpresion.Release();

            // Simula la impresión
            Console.WriteLine($"Asesor {idAsesor} está imprimiendo {numeroFactura}...");
            Thread.Sleep(2000);
            Console.WriteLine($"Asesor {idAsesor} terminó de imprimir {numeroFactura}.");
        }
    }
}
