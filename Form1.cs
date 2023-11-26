using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Runtime.ConstrainedExecution;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;
/* memoria estatica = Tamaño[k] + Asignacion antes Mestatica(compilacion,Tiempode ejeucion)

   Variables Estáticas:  int[] numeros = new int[10];
          TipoDedDato CrearArray NombreVar = InstanciaObj TipoDatos[AsignacionDeMemoria]
            
                           static int contador = 0;
              MiembrodeClaseEstatico TipoDato NomVar = 0;

    Métodos Estáticos:  public static void metodoEstatico() {  operación estática } 
         AccesibleGeneral PerteneceAlaClase NoRetornaValor NombMetodo()             () != Argmentos

    Constantes Estáticas:   public static class Constantes {  public const double PI = 3.14159265359;  }
  AccesibleGeneral PerteneceAlaClase CreandoClase NomClas {  AccesibleGeneral Constante TipoDato NomVar} 

    como formula "public static class V : public const double N = V.N
 */

/* memoria dinamica  = puede agregar o elimitar DATOS (tiempos de Ejecucion) , administra el desarrollador

   
 */
 


namespace U4_memoria
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            ///Es la inicializacion del DataGrid para mostrar los encabezados dentro de la Grid
            dgvProductos.Columns.Add("NombreProducto", "Producto");
            dgvProductos.Columns.Add("PrecioUnitario", "Precio");
            dgvProductos.Columns.Add("Cantidad", "Cantidad");
            dgvProductos.Columns.Add("SubTotal", "Sub Total");

        }
        //////////////////////////////////////////NIVEL DE CLASE //////////////////////////////////////////

        /// <summary>
        /// Declaración de variables a nivel de Clase, nótese que no están dentro de método clic
        /// están al mismo nivel por ello este tipo de declaración es conocida a nivel de Clase
        /// </summary>
        const double IVA = 0.13; // Memoria estática inmutable
        const int LIMITE = 5;   // Memoria estática inmutable
        int item = 0;           // Memoria estática mutable
        /// <summary>
        /// se han declarado arreglos del mismo tipo donde se utilizan las constantes del límite que se tendrán
        /// la variable item es la que servirá en el modelo para saber la posición del elemento
        /// </summary>
        int[] cantidad = new int[LIMITE];
        double[] precio = new double[LIMITE];
        string[] producto = new string[LIMITE];
        //////////////////////////////////////////NIVEL DE CLASE //////////////////////////////////////////

        private void cbxProducto_SelectedIndexChanged(object sender, EventArgs e)
        {
            // Tu código para manejar el evento SelectedIndexChanged
        }
        private void Form1_Load(object sender, EventArgs e)
        {
            // Tu código para manejar el evento Load del formulario
        }

        private void salir_Click(object sender, EventArgs e)
        {
            //Application.Exit();// cerrar la aplicacion
            //Class.metodo
        }

        private void Limpiar_Click(object sender, EventArgs e)
        {
            //dgvProductos.Rows.Clear(); // Elimina todas las filas del DataGridView.

            //txtPU.Text = ""; // Establece el contenido del TextBox en blanco.
           // txtCantidad.Text = ""; // Establece el contenido del TextBox en blanco.
            
           // lblTotal.Text = ""; // Establece el contenido de la etiqueta en blanco.
           // lblIVA.Text = ""; // Establece el contenido de la etiqueta en blanco.

            ////////////////////////////////////////// MEMORIA estatica //////////////////////////////////////////
            ///////////////////////////////////////////// MEMORIA estatica //////////////////////////////////////////

        }
        private void btnAdd_Click(object sender, EventArgs e)
        {
            ///se comienza con inicializaciones y validaciones de entrada
            bool esNumero = false;//establenciendo La Variable False

            if (item >= LIMITE)//cuando se supere el LIMITE
            {
                MessageBox.Show("Sobrepasa el limite permitido");
                return;
            }
            producto[item] = cbxProducto.SelectedItem.ToString();//toma el Valor Seleccionado en el cuadro de producto
                                                                 //lo convierte a texto y lo almacena en la matriz producto en el sub-indice (ITEM)

            esNumero = double.TryParse(txtPU.Text, out precio[item]);// extrae del cuadro el numero en forma de Texto y lo convierte a Double y almacena
                                                                     //  en Matriz Precio en el sub-indice ITEM , si es correcto , esNumero permanece FALSE
            if (!esNumero)
            {
                MessageBox.Show("Ingrese un Precio Valido");
                return;
            }
            esNumero = int.TryParse(txtCantidad.Text, out cantidad[item]);// extrae del cuadro el numero en forma de Texto y lo convierte a Double y almacena
                                                                          //  en Matriz cantidad en el sub-indice ITEM , si es correcto , esNumero permanece FALSE
            if (!esNumero)
            {
                MessageBox.Show("Ingrese una Cantidad Valida");
                return;
            }
            //una vez guardada la información aumentamos en uno para tener la siguiente posición del elemento
             item++;
            MessageBox.Show("Producto Agregado Satistactoriamente");
        }
        ////////////////////////////////////////// MEMORIA estatica //////////////////////////////////////////
        ///////////////////////////////////////////// MEMORIA estatica //////////////////////////////////////////
        private void btnMostrar_Click(object sender, EventArgs e)
        {
            ///Esta parte se hizo con la finalidad de demostrar cómo se recorre un arreglo
            ///se inicializarán las variables resumen para evitar que almacene basura
            double total = 0;
            double totalIVA = 0;
            ///Limpiar los elementos del datagrid
            dgvProductos.Rows.Clear();
            for (int elemento = 0; elemento < LIMITE; elemento++)
            {
                double subTotal = 0;
                subTotal = precio[elemento] * cantidad[elemento];
                total += subTotal;
                ///Agrega el elemento dentro del datagrid para que sean mostrados
                dgvProductos.Rows.Add(producto[elemento], precio[elemento],cantidad[elemento], subTotal);
            }
            ///una vez recorrido todos los elementos se calcula el IVA
            totalIVA = total * IVA;
            ///Después de calculado el IVA se usa la misma variable para que el total se le agregue el IVA
            total = total + totalIVA;
            lblTotal.Text = total.ToString();//incorporando al LABEL en texto,la variable convertida en String 
            lblIVA.Text = totalIVA.ToString();//incorporando al LABEL en texto,la variable convertida en String 
        }       
    }
}
 