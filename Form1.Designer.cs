namespace U4_memoria
{
    partial class Form1
    {
        /// <summary>
        /// Variable del diseñador necesaria.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Limpiar los recursos que se estén usando.
        /// </summary>
        /// <param name="disposing">true si los recursos administrados se deben desechar; false en caso contrario.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Código generado por el Diseñador de Windows Forms

        /// <summary>
        /// Método necesario para admitir el Diseñador. No se puede modificar
        /// el contenido de este método con el editor de código.
        /// </summary>
        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.txtPU = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.txtCantidad = new System.Windows.Forms.TextBox();
            this.hhhh = new System.Windows.Forms.Label();
            this.btnAdd = new System.Windows.Forms.Button();
            this.gbxEntrada = new System.Windows.Forms.GroupBox();
            this.cbxProducto = new System.Windows.Forms.ComboBox();
            this.btnMostrar = new System.Windows.Forms.Button();
            this.gbxTotal = new System.Windows.Forms.GroupBox();
            this.lblIVA = new System.Windows.Forms.Label();
            this.lblTotal = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.dgvProductos = new System.Windows.Forms.DataGridView();
            this.Salir = new System.Windows.Forms.Button();
            this.Limpiar = new System.Windows.Forms.Button();
            this.gbxEntrada.SuspendLayout();
            this.gbxTotal.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvProductos)).BeginInit();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(4, 19);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(100, 13);
            this.label1.TabIndex = 7;
            this.label1.Text = "Seleccion Producto";
            // 
            // txtPU
            // 
            this.txtPU.Location = new System.Drawing.Point(127, 41);
            this.txtPU.Name = "txtPU";
            this.txtPU.Size = new System.Drawing.Size(100, 20);
            this.txtPU.TabIndex = 9;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(4, 44);
            this.label2.Name = "label2";
            this.label2.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.label2.Size = new System.Drawing.Size(117, 13);
            this.label2.TabIndex = 10;
            this.label2.Text = "Precio Unitario(Sin IVA)";
            // 
            // txtCantidad
            // 
            this.txtCantidad.Location = new System.Drawing.Point(126, 65);
            this.txtCantidad.Name = "txtCantidad";
            this.txtCantidad.Size = new System.Drawing.Size(100, 20);
            this.txtCantidad.TabIndex = 12;
            // 
            // hhhh
            // 
            this.hhhh.AutoSize = true;
            this.hhhh.Location = new System.Drawing.Point(23, 68);
            this.hhhh.Name = "hhhh";
            this.hhhh.Size = new System.Drawing.Size(49, 13);
            this.hhhh.TabIndex = 13;
            this.hhhh.Text = "Cantidad";
            // 
            // btnAdd
            // 
            this.btnAdd.Location = new System.Drawing.Point(240, 18);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(79, 63);
            this.btnAdd.TabIndex = 14;
            this.btnAdd.Text = "Agregar";
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
            // 
            // gbxEntrada
            // 
            this.gbxEntrada.Controls.Add(this.cbxProducto);
            this.gbxEntrada.Controls.Add(this.btnAdd);
            this.gbxEntrada.Controls.Add(this.hhhh);
            this.gbxEntrada.Controls.Add(this.txtCantidad);
            this.gbxEntrada.Controls.Add(this.label2);
            this.gbxEntrada.Controls.Add(this.txtPU);
            this.gbxEntrada.Controls.Add(this.label1);
            this.gbxEntrada.Location = new System.Drawing.Point(12, 12);
            this.gbxEntrada.Name = "gbxEntrada";
            this.gbxEntrada.Size = new System.Drawing.Size(342, 91);
            this.gbxEntrada.TabIndex = 5;
            this.gbxEntrada.TabStop = false;
            this.gbxEntrada.Text = "Ingreso de Producto(memoria ESTATICA)";
            // 
            // cbxProducto
            // 
            this.cbxProducto.BackColor = System.Drawing.SystemColors.ScrollBar;
            this.cbxProducto.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cbxProducto.FormattingEnabled = true;
            this.cbxProducto.Items.AddRange(new object[] {
            "Monitor",
            "Teclado",
            "Mouse",
            "Otros"});
            this.cbxProducto.Location = new System.Drawing.Point(126, 16);
            this.cbxProducto.Name = "cbxProducto";
            this.cbxProducto.Size = new System.Drawing.Size(100, 21);
            this.cbxProducto.TabIndex = 18;
            this.cbxProducto.SelectedIndexChanged += new System.EventHandler(this.cbxProducto_SelectedIndexChanged);
            // 
            // btnMostrar
            // 
            this.btnMostrar.Location = new System.Drawing.Point(46, 65);
            this.btnMostrar.Name = "btnMostrar";
            this.btnMostrar.Size = new System.Drawing.Size(157, 23);
            this.btnMostrar.TabIndex = 15;
            this.btnMostrar.Text = "Mostrar Total";
            this.btnMostrar.UseVisualStyleBackColor = true;
            this.btnMostrar.Click += new System.EventHandler(this.btnMostrar_Click);
            // 
            // gbxTotal
            // 
            this.gbxTotal.Controls.Add(this.lblIVA);
            this.gbxTotal.Controls.Add(this.lblTotal);
            this.gbxTotal.Controls.Add(this.btnMostrar);
            this.gbxTotal.Controls.Add(this.label4);
            this.gbxTotal.Controls.Add(this.label5);
            this.gbxTotal.Location = new System.Drawing.Point(366, 12);
            this.gbxTotal.Name = "gbxTotal";
            this.gbxTotal.Size = new System.Drawing.Size(266, 91);
            this.gbxTotal.TabIndex = 15;
            this.gbxTotal.TabStop = false;
            this.gbxTotal.Text = "Total";
            // 
            // lblIVA
            // 
            this.lblIVA.AutoSize = true;
            this.lblIVA.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblIVA.Cursor = System.Windows.Forms.Cursors.AppStarting;
            this.lblIVA.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblIVA.ForeColor = System.Drawing.Color.Red;
            this.lblIVA.Location = new System.Drawing.Point(153, 39);
            this.lblIVA.Name = "lblIVA";
            this.lblIVA.Size = new System.Drawing.Size(29, 15);
            this.lblIVA.TabIndex = 17;
            this.lblIVA.Text = "IVA";
            // 
            // lblTotal
            // 
            this.lblTotal.AutoSize = true;
            this.lblTotal.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblTotal.Cursor = System.Windows.Forms.Cursors.AppStarting;
            this.lblTotal.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTotal.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(0)))), ((int)(((byte)(192)))));
            this.lblTotal.Location = new System.Drawing.Point(142, 14);
            this.lblTotal.Name = "lblTotal";
            this.lblTotal.Size = new System.Drawing.Size(86, 15);
            this.lblTotal.TabIndex = 16;
            this.lblTotal.Text = "Total a Pagar";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(70, 41);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(24, 13);
            this.label4.TabIndex = 10;
            this.label4.Text = "IVA";
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(23, 16);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(97, 13);
            this.label5.TabIndex = 7;
            this.label5.Text = "Total a Pagar +IVA";
            // 
            // dgvProductos
            // 
            this.dgvProductos.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvProductos.Location = new System.Drawing.Point(12, 109);
            this.dgvProductos.Name = "dgvProductos";
            this.dgvProductos.Size = new System.Drawing.Size(599, 234);
            this.dgvProductos.TabIndex = 17;
            // 
            // Salir
            // 
            this.Salir.Location = new System.Drawing.Point(701, 282);
            this.Salir.Name = "Salir";
            this.Salir.Size = new System.Drawing.Size(88, 24);
            this.Salir.TabIndex = 4;
            this.Salir.Text = "salir";
            this.Salir.UseVisualStyleBackColor = true;
            this.Salir.Click += new System.EventHandler(this.salir_Click);
            // 
            // Limpiar
            // 
            this.Limpiar.Location = new System.Drawing.Point(701, 236);
            this.Limpiar.Name = "Limpiar";
            this.Limpiar.Size = new System.Drawing.Size(88, 25);
            this.Limpiar.TabIndex = 3;
            this.Limpiar.Text = "limpiar";
            this.Limpiar.UseVisualStyleBackColor = true;
            this.Limpiar.Click += new System.EventHandler(this.Limpiar_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(826, 645);
            this.Controls.Add(this.dgvProductos);
            this.Controls.Add(this.gbxTotal);
            this.Controls.Add(this.gbxEntrada);
            this.Controls.Add(this.Salir);
            this.Controls.Add(this.Limpiar);
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.gbxEntrada.ResumeLayout(false);
            this.gbxEntrada.PerformLayout();
            this.gbxTotal.ResumeLayout(false);
            this.gbxTotal.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvProductos)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox txtPU;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox txtCantidad;
        private System.Windows.Forms.Label hhhh;
        private System.Windows.Forms.Button btnAdd;
        private System.Windows.Forms.GroupBox gbxEntrada;
        private System.Windows.Forms.Button btnMostrar;
        private System.Windows.Forms.GroupBox gbxTotal;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.DataGridView dgvProductos;
        private System.Windows.Forms.ComboBox cbxProducto;
        private System.Windows.Forms.Label lblIVA;
        private System.Windows.Forms.Label lblTotal;
        private System.Windows.Forms.Button Salir;
        private System.Windows.Forms.Button Limpiar;
    }
}

