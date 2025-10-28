import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-layout',
  imports: [RouterModule, RouterOutlet, TranslateModule],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent {
  constructor(private translate: TranslateModule) {
    
  }

  pageTitle = "Layout";
  sidebar: HTMLElement | null = null;
  pageWidth = 0;
  pageHeight = 0;

  switchSidebar(f: boolean | null = null) {
    const extended = this.sidebar?.classList.contains("extended");
    if (f == null) {
      f = !extended;
    }

    if (f) {
      console.log("EXTEND");
      this.sidebar?.classList.add("extended");
    } else {
      console.log("DE EXTEND");
      this.sidebar?.classList.remove("extended");
    }

  }

  handleSizeChange(w: number, h: number) {
    if (w > 900) {
      if (w < 1000) {
        this.switchSidebar(false);
      } else {
        this.switchSidebar(true);
      }
    } else {
      this.switchSidebar(false);
    }

    this.sidebar!.style.display = "flex";
  }

  linkClicked() {
    if (this.pageWidth <= 900) {
      this.switchSidebar(false);
    }
  }

  mainClicked() {
    const extended = this.sidebar?.classList.contains("extended");

    if (extended && this.pageWidth <= 900) {
      this.switchSidebar(false);
    }
  }

  ngOnInit() {
    this.sidebar = document.querySelector("aside.sidebar");

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        this.pageWidth = width;
        this.pageHeight = height;
        this.handleSizeChange(width, height);
      }
    });

    resizeObserver.observe(document.body);
    this.handleSizeChange(document.body.clientWidth, document.body.clientHeight);
  }

}

